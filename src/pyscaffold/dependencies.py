"""Internal library for manipulating package dependencies and requirements."""

from itertools import chain

from setuptools_scm.version import VERSION_CLASS

from .exceptions import OldSetuptools

try:
    from pkg_resources import parse_version
    from setuptools import __version__ as setuptools_ver
except ImportError:
    raise OldSetuptools


SETUPTOOLS_VERSION = parse_version("38.3")
BUILD_DEPS = {
    "setuptools_scm": parse_version("4.1.2"),
    "wheel": parse_version("0.34.2"),
}
"""dict containing dependencies during build time (``setup_requires``) for PyScaffold.
The keys are package names as found in PyPI, and the values are versions parsed by
:obj:`setuptools_scm.parse_version`.
"""


def check_setuptools_version():
    """Check minimum required version of setuptools

    Check that setuptools has all necessary capabilities for setuptools_scm
    as well as support for configuration with the help of ``setup.cfg``.

    Raises:
          :obj:`OldSetuptools` : raised if necessary capabilities are not met
    """
    setuptools_too_old = parse_version(setuptools_ver) < SETUPTOOLS_VERSION
    setuptools_scm_check_failed = VERSION_CLASS is None
    if setuptools_too_old or setuptools_scm_check_failed:
        raise OldSetuptools


def semantic_dependency(package, version):
    """Create a semantic version compatible dependency range string.

    Args:
        package(str): identifier of the dependency (as in PyPI)
        version: version object as returned by :obj:`pkg_resources.parse_version`
            (``MAJOR.MINOR.PATCH``)

    Returns:
        str: requirement string of a single dependency for ``setup_requires``
            or ``install_requires``.

    Example:

        >>> from pkg_resources import parse_version
        >>> from pyscaffold.utils import semantic_dependency
        >>> semantic_dependency("pyscaffold", parse_version("3.2.1")
        "pyscaffold>=3.2.1,<4.0"
    """
    require_str = "{package}>={major}.{minor}.{patch},<{next_major}.0"
    major, minor, patch, *_rest = version.base_version.split(".")
    next_major = int(major) + 1
    return require_str.format(
        package=package, major=major, minor=minor, patch=patch, next_major=next_major
    )


def is_included(require_str, deps=BUILD_DEPS):
    """Given an individual dependency requirement string (e.g.
    ``"pyscaffold>=3.2.1,4.0"``), returns ``True`` if that dependency is already
    included in ``deps``.

    ``deps`` should be a list with package names (as in PyPI) or a dict with
    them as keys (without version numbers).
    """
    return any(require_str.startswith(dep) for dep in deps)


def split(require_str):
    """Split a combined requirement string (such as the values for ``setup_requires``
    and ``install_requires`` in ``setup.cfg``) into a list of individual requirement
    strings, that can be used in :obj:`is_included`, :obj:`get_requirements_str`,
    :obj:`remove`, etc...
    """
    deps = (dep.strip() for line in require_str.splitlines() for dep in line.split(";"))
    return [dep for dep in deps if dep]  # Remove empty deps


def remove(require_list, to_remove):
    """Given a list of individual requirement strings, e.g.  ``["appdirs>=1.4.4",
    "packaging>20.0"]``, remove the dependencies in ``to_remove`` (list of dependency
    names without the version, or dict with those as keys).
    """
    return [dep for dep in require_list if not is_included(dep, to_remove)]


def get_requirements_str(
    extra_deps=(), own_deps=BUILD_DEPS, separator="\n    ", start="\n    ", end=""
):
    """Determines a proper requirement string for PyScaffold.
    When no argument is given, will produce a value suitable for PyScaffold's
    ``setup_requires``.

    Args:
        extra_deps (List[str]): list of individual requirement strings (e.g.
            ``["appdirs>=1.4.4", "packaging>20.0"]``) in addition to ``own_deps``
            (if already in ``own_deps`` will be ignored). Empty by default.
        own_deps (dict): mapping between package name (as in PyPI) and the output of
            :obj:`pkg_resources.parse_version`. This is meant to be the internal set of
            dependencies required (or being added).
            The versions will be converted to a semantic version compatible range.
            By default will be equivalent to PyScaffold's :obj:`build dependencies
            <~.BUILD_DEPS>`.
        separator (str): string that will be used to combine all dependencies.
        start (str): string to be added to the beginning of the combined requirement.
        end (str): string to be added to the end of the combined requirement.

    Returns:
        str: requirement string, e.g.::

                setuptools_scm>=4.1.2,<5.0"
                pyscaffold>=0.34.3,<1.0"
    """
    # Remove any given deps that will already be added by PyScaffold
    deduplicated = remove(extra_deps, own_deps)
    minimal_deps = (semantic_dependency(k, v) for k, v in own_deps.items())
    deps = separator.join(chain(minimal_deps, deduplicated))
    return start + deps + end if deps else ""
