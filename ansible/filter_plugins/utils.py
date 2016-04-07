import os


def lookupValue(value, arg):
    result = value
    for key in arg.split("."):
        result = result[key]
    return result


def lastPath(value):
    return os.path.basename(os.path.normpath(value))


class FilterModule(object):

    filter_map =  {
        'lookupValue': lookupValue,
        'lastPath':lastPath
    }

    def filters(self):
        return self.filter_map
