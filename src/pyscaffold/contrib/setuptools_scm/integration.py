from pkg_resources import iter_entry_points

from .version import _warn_if_setuptools_outdated
from .utils import do
from . import get_version


def version_keyword(dist, keyword, value):
    _warn_if_setuptools_outdated()
    if not value:
        return
    if value is True:
        value = {}
    if getattr(value, "__call__", None):
        value = value()

    dist.metadata.version = get_version(**value)


def find_files(path=""):
    for ep in iter_entry_points("setuptools_scm.files_command"):
        command = ep.load()
        if isinstance(command, str):
            # this technique is deprecated
            res = do(ep.load(), path or ".").splitlines()
        else:
            res = command(path)
        if res:
            return res
    return []
