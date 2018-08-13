from pkg_resources import iter_entry_points

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
    if getattr(value, "__call__", None):
        value = value()
    # this piece of code is a hack to counter the mistake in root finding
    matching_fallbacks = iter_matching_entrypoints(
        ".", "setuptools_scm.parse_scm_fallback"
    )
    if any(matching_fallbacks):
        value.pop("root", None)
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
