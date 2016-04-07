import os
import glob
import datetime

from subprocess import Popen, PIPE
from pythoncliutil import cron_command, request_input, request_continue

from fabric.api import env, sudo, run, cd, local, put, prefix, roles, execute, task, get
from fabric.api import settings as fab_settings
from fabric.context_managers import settings, hide
from fabric.contrib.files import sed

from utils import _build_env, _run_task, _cron_command, _request_input, _request_continue, _append_to_file, _load_template

from enumerations import GEONODE_TYPES, ISO_CATEGORIES

global targets
targets = ()

PATH_ACTIVATE = "/var/lib/geonode/bin/activate"
PATH_MANAGEPY_VN = "/var/lib/geonode"
PATH_MANAGEPY_GS = "/var/lib/geonode/rogue_geonode"

PATH_DNA_JSON = "/opt/chef-run/dna.json"

PATH_LS_VN = "/var/lib/geonode/local_settings.py"
PATH_LS_GS = "/var/lib/geonode/rogue_geonode/geoshape/local_settings.py"

PATH_GEOSERVER_DATA = "/var/lib/geoserver_data"

#############################################################
# The Public API
@task
def gn(*args):
    """
    Load GeoNode settings from geonodes.py

    Imports GeoNode settings from a geonodes.py file
    in the same directory
    """
    global targets
    targets = args


@task
def host_type(*args):
    return _run_task(_host_type, args=args)


@task
def lsb_release(*args):
    return _run_task(_lsb_release, args=args)

## GeoSever

@task
def restart_geoserver(*args):
    return _run_task(_restart_geoserver, args=args)


@task
def cron_restart_geoserver(frequency):
    return _run_task(_cron_restart_geoserver, args=[frequency])


## Vanilla

@task
def updatelayers_vanilla(*args):
    return _run_task(_updatelayers_vanilla, args=args)


## GeoSHAPE


@task
def provision_geoshape(*args):
    """
    Provision a GeoSHAPE instance

    Runs `cybergis-scripts-rogue.sh prod provision`
    """

    return _run_task(_provision_geoshape, args=args)


@task
def restart_geoshape(*args):
    """
    Restart GeoSHAPE instance, including Django, GeoServer, and RabbitMQ

    Calls ./stop_geonode and ./start_geonode,
    restarts tomcat7, and resets RabbitMQ
    """

    return _run_task(_restart_geoshape, args=args)


@task
def inspect_geoshape(*args):
    return _run_task(_inspect_geoshape, args=args)


@task
def updatelayers_geoshape(*args):
    return _run_task(_updatelayers_geoshape, args=args)


@task
def importlayers(t=None, local=None, drop=None, user=None, overwrite=None, category=None, keywords=None, private=None):
    """
    Import local files into a GeoNode instance

    Puts via SFTP local files into the remote's "drop" folder and then
    runs importlayers on all of them.

    Options:
    t = GeoNode Type (Vanilla or GeoSHAPE)
    local = local file path
    drop = temporary drop folder

    user = the user that will own the layer
    overwrite = overwrite existing layers
    category = ISO Category for layer
    keywords = comma separated list of keywords
    private = Is layer only visible to owner and admins?
    """

    return _run_task(_importlayers, kwargs={'t':t, 'local':local, 'drop': drop, 'user': user, 'overwrite': overwrite, 'category': category, 'keywords': keywords, 'private': private})


@task
def add_gmail(t=None, u=None, p=None):
    """
    Adds server GMail to instance

    Adds GMail settings to vim /var/lib/geonode/rogue_geonode/geoshape/local_settings.py

    """

    address = _request_input("User", u, True)+'@gmail.com'
    host = 'smtp.gmail.com'
    return _run_task(_add_email, args=None, kwargs={'t':t, 'a':address, 'p':p, 'h':host})

@task
def add_analytics_ga(t=None, c=None):
    return _run_task(_add_analytics_ga, args=None, kwargs={'t':t, 'c':c})


@task
def add_analytics_dap(t=None, a=None, sa=None):
    return _run_task(_add_analytics_dap, args=None, kwargs={'t':t, 'a':a, 'sa':sa})


@task
def backup_geonode(t=None, remote=None, local=None):
    """
    Backup GeoNode to disk

    Backs up GeoNode to the destination "d" folder
    on disk.

    Options:
    t = GeoNode Type (Vanilla or GeoSHAPE)
    remote = remote folder to backup to (required)
    local = local folder to backup to (optional)
    """

    return _run_task(_backup_geonode, args=None, kwargs={'t':t, 'remote':remote, 'local':local})

#############################################################
# The Private API

def _host_type():
    run('uname -s')


def _lsb_release():
    run('lsb_release -c')


def _host_type():
    run('uname -s')


def _restart_geoserver():
    sudo('/etc/init.d/tomcat7 restart')


def _cron_restart_geoserver(frequency):
    cmd = _cron_command(f=frequency, u ='root', c='/etc/init.d/tomcat7 restart', filename='geoserver_restart')
    print cmd
    sudo(cmd)


def _restart_apache2():
    sudo('/etc/init.d/apache2 restart')


def _restart_nginx():
    sudo('/etc/init.d/nginx restart')


def _restart_rabbitmq():
    sudo('rabbitmqctl stop_app')
    sudo('rabbitmqctl reset')
    sudo('rabbitmqctl start_app')


def _restart_geoshape():
    with cd("/var/lib/geonode/rogue_geonode/scripts"):
        sudo('./stop_geonode.sh')
        sudo('./start_geonode.sh')

    _restart_geoserver()
    _restart_rabbitmq()


def _inspect_geoshape():
    sudo('lsb_release -c')
    sudo('cat '+PATH_DNA_JSON)
    sudo('tail -n 20 /var/log/kern.log')


def _updatelayers_vanilla():
    _updatelayers(PATH_MANAGEPY_VN, PATH_ACTIVATE)


def _updatelayers_geoshape():
    _updatelayers(PATH_MANAGEPY_GS, PATH_ACTIVATE)


def _updatelayers(current_directory, activate):
    with cd(current_directory):
        t = "source {a}; python manage.py updatelayers"
        c = t.format(a=activate)
        sudo(c)

def _importlayers(t=None, local=None, drop=None, user=None, overwrite=None, category=None, keywords=None, private=None):

    t = _request_input("Type (vanilla/geoshape)", t, True, options=GEONODE_TYPES)
    local = _request_input("Local File Path", local, True)
    drop = _request_input("Remote Drop Folder", drop, True)

    user = _request_input("User", user, False)
    overwrite = _request_input("Overwrite", overwrite, False)
    category = _request_input("Category", category, False, options=ISO_CATEGORIES)
    keywords = _request_input("Keywords (Comma-separated)", keywords, False)
    private = _request_input("Private", private, True)

    path_managepy = PATH_MANAGEPY_GS if t.lower()=="geoshape" else PATH_MANAGEPY_VN

    if _request_continue():
        sudo("[ -d {d} ] || mkdir {d}".format(d=drop))
        remote_files = put(local, drop, mode='0444', use_sudo=True)
        if remote_files:
            with cd(path_managepy):
                template = "source {a}; python manage.py importlayers {paths}"
                if user:
                    template += " -u {u}".format(u=user)
                if overwrite:
                    template += " -o"
                if category:
                    template += " -c {c}".format(c=category)
                if keywords:
                    template += " -k {kw}".format(kw=keywords)
                if private:
                    template += " -p"
                c = template.format(a=PATH_ACTIVATE, paths=(" ".join(remote_files)))
                sudo(c)
        else:
            print "Not files uploaded"


def _provision_geoshape():
    sudo('cat '+PATH_DNA_JSON)
    sudo("cybergis-scripts-rogue.sh prod provision")

def _add_email(t=None, a=None, p=None, h=None):

    data = _load_template('settings_email.py')
    if data:
        t = _request_input("Type (vanilla/geoshape)", t, True, options=GEONODE_TYPES)
        a = _request_input("Address (e.g., john@gmail.com)", a, True)
        p = _request_input("Password", p, True)
        h = _request_input("Host (e.g., smtp.gmail.com)", h, True)

        ls = PATH_LS_GS if t.lower()=="geoshape" else PATH_LS_VN
        data = data.replace("{{address}}", a)
        data = data.replace("{{password}}", p)
        data = data.replace("{{host}}", h)

        print "Local Settings: "+ls
        print "Data..."
        print data

        if _request_continue():
            _append_to_file(data.split("\n"), ls)


def _add_analytics_dap(t=None, a=None, sa=None):

    data = _load_template('settings_dap.py')
    if data:
        t = _request_input("Type (vanilla/geoshape)", t, True, options=GEONODE_TYPES)
        a = _request_input("Agency", a, True)
        sa = _request_input("Sub-agency", sa, True)

        ls = PATH_LS_GS if t.lower()=="geoshape" else PATH_LS_VN
        data = data.replace("{{agency}}", a)
        data = data.replace("{{subagency}}", sa)

        print "Local Settings: "+ls
        print "Data..."
        print data

        if _request_continue():
            _append_to_file(data.split("\n"), ls)


def _add_analytics_ga(t=None, c=None):

    data = _load_template('settings_ga.py')
    if data:
        t = _request_input("Type (vanilla/geoshape)", t, True, options=GEONODE_TYPES)
        c = _request_input("Code", c, True)

        ls = PATH_LS_GS if t.lower()=="geoshape" else PATH_LS_VN
        data = data.replace("{{code}}", c)

        print "Local Settings: "+ls
        print "Data..."
        print data

        if _request_continue():
            _append_to_file(data.split("\n"), ls)


def _backup_geonode(t=None, remote=None, local=None):

    t = _request_input("Type (vanilla/geoshape)", t, True, options=GEONODE_TYPES)
    remote = _request_input("Remote Destination Folder", remote, True)
    local = _request_input("Local File Path", local, False)

    if _request_continue():

        print "Backing up data..."

        sudo("[ -d {d} ] || mkdir {d}".format(d=remote))
        sudo("[ -d {d}/db ] || mkdir {d}/db".format(d=remote))
        sudo('chown -R {u}:{g} {d}/db'.format(u="postgres", g="postgres", d=remote))
        with settings(sudo_user='postgres'):
            sudo('pg_dump geonode | gzip > {d}/db/geonode.gz'.format(d=remote))
            sudo('pg_dump geonode_imports | gzip > {d}/db/geonode_imports.gz'.format(d=remote))
        sudo('cp -R {gsd} {d}/geoserver'.format(gsd=PATH_GEOSERVER_DATA, d=remote))

        if local:
            local_files = get(remote, local_path=local)
            for local_file in local_files:
                print "Downloaded Local File: "+local_file

        print "Backup complete."
