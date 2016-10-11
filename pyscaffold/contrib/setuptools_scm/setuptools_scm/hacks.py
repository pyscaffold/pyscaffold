import os
from .utils import data_from_mime, trace
from .version import meta


def parse_pkginfo(root):

    pkginfo = os.path.join(root, 'PKG-INFO')
    trace('pkginfo', pkginfo)
    data = data_from_mime(pkginfo)
    version = data.get('Version')
    if version != 'UNKNOWN':
        return meta(version)
