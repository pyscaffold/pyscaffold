"""Internal library for manipulating package dependencies and requirements."""

import re
from itertools import chain
from typing import Iterable, List

from setuptools_scm.version import VERSION_CLASS

from .exceptions import OldSetuptools

try:
    from pkg_resources import Requirement, parse_version
    from setuptools import __version__ as setuptools_ver
except ImportError:
    raise OldSetuptools


SETUPTOOLS_VERSION = parse_version("38.3")
BUILD = ["setuptools_scm>=4.1.2,<5", "wheel>=0.34.2,<1"]
"""Dependencies that will be required to build the created project"""

REQ_SPLITTER = re.compile(r";(?!(python|platform|implementation|os|sys)_)", re.I | re.M)
"""Regex to split requirements that considers both `setup.cfg specs`_ and `PEP 508`_
(in *good enough* a simplified fashion).

.. _setup.cfg specs: https://setuptools.readthedocs.io/en/latest/setuptools.html#options
.. _PEP 508: https://www.python.org/dev/peps/pep-0508/
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
    """Given a sequence of individual requirement strings, e.g. ``["appdirs>=1.4.4",
    "packaging>20.0"]``, remove the duplicated packages.
    If a package is duplicated, the last occurrence stays.
    """
    return list({Requirement.parse(r).key: r for r in requirements}.values())


def remove(requirements: Iterable[str], to_remove: Iterable[str]) -> List[str]:
    """Given a list of individual requirement strings, e.g.  ``["appdirs>=1.4.4",
    "packaging>20.0"]``, remove the requirements in ``to_remove``.
    """
    removable = {Requirement.parse(r).key for r in to_remove}
    return [r for r in requirements if Requirement.parse(r).key not in removable]


def add(requirements: Iterable[str], to_add: Iterable[str] = BUILD) -> List[str]:
    """Given a sequence of individual requirement strings, add ``to_add`` to it.
    By default adds :obj:`BUILD` if ``to_add`` is not given."""
    return deduplicate(chain(requirements, to_add))
