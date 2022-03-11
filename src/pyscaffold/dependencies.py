"""Internal library for manipulating package dependencies and requirements."""

import re
from itertools import chain
from typing import Iterable, List

from packaging.requirements import InvalidRequirement, Requirement

# setuptools version is now enforced via `install_requires`

BUILD = ("setuptools_scm>=5", "wheel")
"""Dependencies that will be required to build the created project"""
RUNTIME = ('importlib-metadata; python_version<"3.8"',)
# TODO: Remove `importlib-metadata` when `python_requires = >= 3.8`
"""Dependencies that will be required at runtime by the created project"""
ISOLATED = ("setuptools>=46.1.0", "setuptools_scm[toml]>=5", *BUILD[1:])
"""Dependencies for isolated builds (PEP517/518).
- setuptools min version might be slightly higher then the version required at runtime.
- setuptools_scm requires an optional dependency to work with pyproject.toml
"""
# Although version 36.6.0 introduces PEP517 implementation,
# version 46.1.0 fix a bug with setuptools.finalize_distribution_options,
# which is a hook used by setuptools_scm (better safe then sorry).

# TODO: Maybe specify a min version for wheel?
#       For the time being, there is an issue preventing us to do that:
#       https://github.com/pypa/pep517/issues/86

REQ_SPLITTER = re.compile(r";(?!\s*(python|platform|implementation|os|sys)_)", re.M)
"""Regex to split requirements that considers both `setup.cfg specs`_ and `PEP 508`_
(in a *good enough* simplified fashion).

.. _setup.cfg specs: https://setuptools.pypa.io/en/latest/userguide/declarative_config.html
.. _PEP 508: https://www.python.org/dev/peps/pep-0508/
"""  # noqa


def split(requirements: str) -> List[str]:
    """Split a combined requirement string (such as the values for ``setup_requires``
    and ``install_requires`` in ``setup.cfg``) into a list of individual requirement
    strings, that can be used in :obj:`is_included`, :obj:`get_requirements_str`,
    :obj:`remove`, etc...
    """
    lines = requirements.splitlines()
    deps = (dep.strip() for line in lines for dep in REQ_SPLITTER.split(line) if dep)
    return [dep for dep in deps if dep]  # Remove empty deps


def deduplicate(requirements: Iterable[str]) -> List[str]:
    """Given a sequence of individual requirement strings, e.g.
    ``["platformdirs>=1.4.4", "packaging>20.0"]``, remove the duplicated packages.
    If a package is duplicated, the last occurrence stays.
    """
    return list({attempt_pkg_name(r): r for r in requirements}.values())


def remove(requirements: Iterable[str], to_remove: Iterable[str]) -> List[str]:
    """Given a list of individual requirement strings, e.g. ``["platformdirs>=1.4.4",
    "packaging>20.0"]``, remove the requirements in ``to_remove``.
    """
    removable = {attempt_pkg_name(r) for r in to_remove}
    return [r for r in requirements if attempt_pkg_name(r) not in removable]


def add(requirements: Iterable[str], to_add: Iterable[str] = BUILD) -> List[str]:
    """Given a sequence of individual requirement strings, add ``to_add`` to it.
    By default adds :obj:`BUILD` if ``to_add`` is not given."""
    return deduplicate(chain(requirements, to_add))


def attempt_pkg_name(requirement: str) -> str:
    """In the case the given string is a dependency specification (PEP 508/440),
    it returns the "package name" part of dependency (without versions).
    Otherwise, it returns the same string (removed the comment marks).
    """
    req = requirement.strip("#").strip()
    try:
        return Requirement(req).name
    except InvalidRequirement:
        return req
