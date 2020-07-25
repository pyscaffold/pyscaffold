"""
Miscellaneous utilities and tools
"""

import keyword
import re
from itertools import chain

from pkg_resources import parse_version

from setuptools_scm.version import VERSION_CLASS

from .exceptions import InvalidIdentifier, OldSetuptools

SETUPTOOLS_VERSION = parse_version("38.3")
BUILD_DEPS = {
    "setuptools_scm": parse_version("4.1.2"),
    "wheel": parse_version("0.34.2"),
}
"""dict containing dependencies during build time (``setup_requires``) for PyScaffold.
The keys are package names as found in PyPI, and the values are versions parsed by
:obj:`setuptools_scm.parse_version`.
"""


def is_valid_identifier(string):
    """Check if string is a valid package name

    Args:
        string (str): package name

    Returns:
        bool: True if string is valid package name else False
    """
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
    """Try to make a valid package name identifier from a string

    Args:
        string (str): invalid package name

    Returns:
        str: valid package name as string or :obj:`RuntimeError`

    Raises:
        :obj:`InvalidIdentifier`: raised if identifier can not be converted
    """
    string = str(string).strip()
    string = string.replace("-", "_")
    string = string.replace(" ", "_")
    string = re.sub("[^_a-zA-Z0-9]", "", string)
    string = string.lower()
    if is_valid_identifier(string):
        return string
    else:
        raise InvalidIdentifier("String cannot be converted to a valid identifier.")


# from http://en.wikibooks.org/, Creative Commons Attribution-ShareAlike 3.0
def levenshtein(s1, s2):
    """Calculate the Levenshtein distance between two strings

    Args:
        s1 (str): first string
        s2 (str): second string

    Returns:
        int: distance between s1 and s2
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def check_setuptools_version():
    """Check minimum required version of setuptools

    Check that setuptools has all necessary capabilities for setuptools_scm
    as well as support for configuration with the help of ``setup.cfg``.

    Raises:
          :obj:`OldSetuptools` : raised if necessary capabilities are not met
    """
    try:
        from pkg_resources import parse_version
        from setuptools import __version__ as setuptools_ver
    except ImportError:
        raise OldSetuptools

    setuptools_too_old = parse_version(setuptools_ver) < SETUPTOOLS_VERSION
    setuptools_scm_check_failed = VERSION_CLASS is None
    if setuptools_too_old or setuptools_scm_check_failed:
        raise OldSetuptools


def dasherize(word: str) -> str:
    """Replace underscores with dashes in the string.

    Example::

        >>> dasherize("foo_bar")
        "foo-bar"

    Args:
        word (str): input word

    Returns:
        input word with underscores replaced by dashes
    """
    return word.replace("_", "-")


CAMEL_CASE_SPLITTER = re.compile(r"\W+|([A-Z][^A-Z\W]*)")


def underscore(word: str) -> str:
    """Convert CamelCasedStrings or dasherized-strings into underscore_strings.

    Example::

        >>> underscore("FooBar-foo")
        "foo_bar_foo"
    """
    return "_".join(w for w in CAMEL_CASE_SPLITTER.split(word) if w).lower()


def deterministic_name(ext):
    """Private API that returns an string that can be used to deterministically
    reduplicate and sort extensions.
    Not available for use outside PyScaffold's core.
    """
    return ".".join(
        [ext.__module__, getattr(ext, "__qualname__", ext.__class__.__qualname__)]
    )


def deterministic_sort(extensions):
    """Private API that remove duplicates and order a list of extensions
    lexicographically which is needed for determinism, also internal before external:
    "pyscaffold.*" < "pyscaffoldext.*"
    Not available for use outside PyScaffold's core.
    """
    deduplicated = {deterministic_name(e): e for e in extensions}
    # ^  duplicated keys will overwrite each other, so just one of them is left
    return [v for (_k, v) in sorted(deduplicated.items())]


def get_id(function):
    """Given a function, calculate its identifier.

    A identifier is a string in the format ``<module name>:<function name>``,
    similarly to the convention used for setuptools entry points.

    Note:
        This function does not return a Python 3 ``__qualname__`` equivalent.
        If the function is nested inside another function or class, the parent
        name is ignored.

    Args:
        function (callable): function object

    Returns:
        str: identifier
    """
    return "{}:{}".format(function.__module__, function.__name__)


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


def is_dep_included(require_str, deps=BUILD_DEPS):
    """Given an individual dependency requirement string (e.g.
    ``"pyscaffold>=3.2.1,4.0"``), returns ``True`` if that dependency is already
    included in ``deps``.

    ``deps`` should be a list with package names (as in PyPI) or a dict with
    them as keys (without version numbers).
    """
    return any(require_str.startswith(dep) for dep in deps)


def split_deps(require_str):
    """Split a combined requirement string (such as the values for ``setup_requires``
    and ``install_requires`` in ``setup.cfg``) into a list of individual requirement
    strings, that can be used in :obj:`is_dep_included`, :obj:`get_requirements_str`,
    :obj:`remove_deps`, etc...
    """
    deps = (dep.strip() for line in require_str.splitlines() for dep in line.split(";"))
    return [dep for dep in deps if dep]  # Remove empty deps


def remove_deps(require_list, to_remove):
    """Given a list of individual requirement strings, e.g.  ``["appdirs>=1.4.4",
    "packaging>20.0"]``, remove the dependencies in ``to_remove`` (list of dependency
    names without the version, or dict with those as keys).
    """
    return [dep for dep in require_list if not is_dep_included(dep, to_remove)]


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
    deduplicated = remove_deps(extra_deps, own_deps)
    minimal_deps = (semantic_dependency(k, v) for k, v in own_deps.items())
    deps = separator.join(chain(minimal_deps, deduplicated))
    return start + deps + end if deps else ""


def setdefault(dict_ref, key, value):
    """Equivalent to built-in :meth:`dict.setdefault`, but ignores values
    if ``None`` or ``""`` (both existing in the dictionary or as the ``value``
    to set).

    Modifies the original dict and returns a reference to it
    """
    if key in dict_ref and dict_ref[key] not in (None, ""):
        return dict_ref
    if value in (None, ""):
        return dict_ref
    dict_ref[key] = value
    return dict_ref
