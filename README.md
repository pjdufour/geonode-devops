# GeoNode DevOps (geonode-devops)

DevOps tools for developing & deploying [GeoNode](http://geonode.org/), including [Ansible](https://www.ansible.com/), [Packer](https://www.packer.io/), [Vagrant](https://www.vagrantup.com/), and [Fabric](http://www.fabfile.org/) configuration files for building and managing Ubuntu and CentOS GeoNode boxes.

After following the installation steps, continue to [Launch](#launch) section to start up GeoNode.

# Installation

On the control/host machine, you'll need to install [Ansible](https://www.ansible.com/), [Packer](https://www.packer.io/), [Vagrant](https://www.vagrantup.com/), and [Fabric](http://www.fabfile.org).

**Quick Install**

If you wish to use a python virtual environment on your host/control machine, be sure to install `virutalenv` and `virtualenvwrapper`.  Your `~/.bash_aliases` file should look something like the following:

```
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export WORKON_HOME=~/.venvs
source /usr/local/bin/virtualenvwrapper.sh
export PIP_DOWNLOAD_CACHE=$HOME/.pip-downloads
```

To quickly install [Ansible](https://www.ansible.com/) and [Fabric](http://www.fabfile.org), run the following:

```
sudo apt-get install python-dev # if not already installed
sudo easy_install pip  # if pip is not already installed
sudo pip install virtualenv virtualenvwrapper
# cd into project directory
sudo pip install -r requirements.txt
```

## Ansible

Ansible is an agent-less provisioning tool for managing the state of machines.  It is used by both [Packer](https://www.packer.io/) and [Vagrant](https://www.vagrantup.com/).  By sharing a common Ansible `playbook` for configuring production machines, building test boxes via Packer, and development boxes for Vagrant, we're able to have dev-prod parity.

To get [Ansible](https://www.ansible.com/) follow the relevant section below.  Also see http://docs.ansible.com/ansible/intro_installation.html#getting-ansible for more information.

#### Mac OS X & Ubuntu

```
sudo easy_install pip  # if pip is not already installed
sudo pip install ansible
```

## Packer

[Packer](https://www.packer.io/) can be used to build virtual machine images.

#### Mac OS X

```
sudo mkdir -p /opt/packer/bin
cd /opt/packer/
sudo wget https://releases.hashicorp.com/packer/0.10.0/packer_0.10.0_darwin_amd64.zip
sudo unzip packer_0.10.0_darwin_amd64.zip
sudo mv packer /opt/packer/bin
cd /usr/local/bin/
sudo ln -s /opt/packer/bin/packer packer
```

#### Ubuntu

```
sudo mkdir -p /opt/packer/bin
cd /opt/packer/
sudo wget 'https://releases.hashicorp.com/packer/0.10.0/packer_0.10.0_linux_amd64.zip'
sudo unzip packer_0.10.0_linux_amd64.zip
sudo mv packer /opt/packer/bin
cd /usr/bin/
sudo ln -s /opt/packer/bin/packer packer
```

## Fabric

[Fabric](http://www.fabfile.org/) provides an easy command line interface for executing remote shell commands and for transferring files between machines.  Fabric is extremely useful for transferring files and managing remote servers.

Follow directions at http://www.fabfile.org/installing.html to install fabric or follow shortcuts below.

#### Mac OS X & Ubuntu

```
sudo pip install fabric
```

Once fabric is installed, create a `geonodes.py` file in the same directory as the `fabfile.py`.  `geonodes.py` is in `.gitignore` so will not be committed.  This file includes connection and other information, so that fab commands are streamlined.

```javascript
GEONODE_INSTANCES = {
    "devgeonode": {
        "ident":  "~/auth/keys/devgeonode.pem",
        "host": "dev.geonode.example.com",
        "user": "ubuntu",
        "type": "geoshape"
    },
    "prodgeonode": {
        "ident":  "~/auth/keys/prodgeonode.pem",
        "host": "prod.geonode.example.com",
        "user": "ubuntu",
        "type": "geoshape"
    }
}
```

# Usage

Create a `secret.yml` file in the project root.

## Vagrant

To add the Centos 6.4 vagrant box to your control machine, run:

```
vagrant box add --name "centos/6.4" http://developer.nrel.gov/downloads/vagrant-boxes/CentOS-6.4-x86_64-v20131103.box

```

To add an Ubuntu 16.04 LTS ("Xenial") vagrant box to your control machine, run:

```
vagrant box add bento/ubuntu-16.04

```

Do no use `ubuntu/xenial64` from Ubuntu cloud images, as referenced here: https://bugs.launchpad.net/cloud-images/+bug/1569237.

To launch the GeoNode virtual machine run:

```
vagrant up
```

To re-provision the machine run:

```
vagrant provision
```

## Packer

You can also use [Packer](https://www.packer.io/) to build a virtual machine.

To build a base box for CentOS 6.4, run:

```
packer build -var 'ansible_playbook=ansible/centos_base.yml' -var 'ansible_secret=secret.yml' -var 'ansible_os=centos' packer/centos64.json
```

To build a base box for Ubuntu 16.04, run:

```
packer build -var 'ansible_playbook=ansible/ubuntu_base.yml' -var 'ansible_secret=secret.yml' -var 'ansible_os=ubuntu' packer/ubuntu1604.json
```

#### Adding Your New Box

After you created your box, you can add with:

```
vagrant box add --name "geonode_base" packer_virtualbox-ovf_virtualbox.box
```

Add the box to the [Vagrantfile](https://github.com/pjdufour/geonode-devops/blob/master/Vagrantfile) to provision with it.

## Launch

Once the image is provisioned, ssh into the machine via:

```
# cd into geonode-devops.git directory
vagrant ssh
```

Once in the virtual machine, run:

```
workon geonode
cd geonode
paver stop
paver reset_hard
paver setup
paver start -b 0.0.0.0:8000  # Launches Django and GeoServer.  Listens to all addresses on port 8000.
```

## Fabric

[Fabric](http://www.fabfile.org/) provides an easy command line interface for executing remote shell commands and for transferring files between machines.  For GeoNode, Fabric can be used to import large files, `updatelayers`, manage GeoServer restart cron jobs, and backup a remote GeoNode locally.

To get started, change directory (`cd`) into the main fabric directory (`./fabric`) with the `fabfile.py`.  When you call fab, start with `gn:geonodehost` so that the host and identity key are loaded automatically from `geonodes.py`.

To see a list of tasks run:

```
fab -l
```

To see the long description of a task run:

```
fab -d taskname
```

A few examples:

```
fab gn:devgeonode,prodgeonode lsb_release
fab gn:devgeonode inspect_geoshape
fab gn:devgeonode restart_geoshape
fab gn:prodgeonode updatelayers:t=geoshape
fab gn:prodgeonode importlayers:t=geoshape,local=~/data/*.zip,drop=/opt/drop,user=admin,overwrite=1,private=1
fab gn:prodgeonode addgmail_geoshape:email,password
fab gn:prodgeonode cron_restart_geoserver:'00 04 * * *'
fab gn:prodgeonode backup_geonode:t=geoshape,remote=/opt/backups/20150707,local=~/backups
```
