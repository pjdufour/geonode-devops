from urlparse import urlparse

# scheme://netloc/path;parameters?query#fragment

def fqdn(value):
    uri = urlparse(value)
    return uri.netloc

def hostname(value):
    uri = urlparse(value)
    return uri.hostname

def port(value):
    uri = urlparse(value)
    return uri.port

# ---- Ansible filters ----

class FilterModule(object):
    ''' URL manipulation filters '''
    filter_map =  {
        'fqdn': fqdn,
        'hostname': hostname,
        'port': port
    }

    def filters(self):
        if urlparse:
            return self.filter_map
        else:
            return {}
