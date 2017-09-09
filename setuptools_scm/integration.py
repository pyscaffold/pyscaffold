import os

from .version import _warn_if_setuptools_outdated
from .utils import do
from .discover import iter_matching_entrypoints
from . import get_version


def version_keyword(dist, keyword, value):
    _warn_if_setuptools_outdated()
    if not value:
        return
    if value is True:
        value = {}
    if getattr(value, '__call__', None):
        value = value()
    # this piece of code is a hack to counter the mistake in root finding
    matching_fallbacks = iter_matching_entrypoints(
        '.', 'setuptools_scm.parse_scm_fallback')
    if any(matching_fallbacks):
        value.pop('root', None)
    dist.metadata.version = get_version(**value)


def find_files(path='.'):
    if not path:
        path = '.'
    abs = os.path.abspath(path)
    ep = next(iter_matching_entrypoints(
        abs, 'setuptools_scm.files_command'), None)
    if ep:
        command = ep.load()
        try:
            if isinstance(command, str):
                return do(ep.load(), path).splitlines()
            else:
                return command(path)
        except Exception:
            import traceback
            print("File Finder Failed for %s" % ep)
            traceback.print_exc()
            return []

    else:
        return []
