import os
from .utils import data_from_mime, trace
from .version import meta


def parse_pkginfo(root):

    pkginfo = os.path.join(root, 'PKG-INFO')
    trace('pkginfo', pkginfo)
    data = data_from_mime(pkginfo)
    version = data.get('Version')
    if version != 'UNKNOWN':
        return meta(version, preformatted=True)


def parse_pip_egg_info(root):
    pipdir = os.path.join(root, 'pip-egg-info')
    if not os.path.isdir(pipdir):
        return
    items = os.listdir(pipdir)
    trace('pip-egg-info', pipdir, items)
    if not items:
        return
    return parse_pkginfo(os.path.join(pipdir, items[0]))
