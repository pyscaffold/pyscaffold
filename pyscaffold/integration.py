# -*- coding: utf-8 -*-

"""
Integration part for hooking into distutils/setuptools

Rationale:
The ``use_pyscaffold`` keyword is unknown to setuptools' setup(...) command,
therefore the ``entry_points`` are checked for a function to handle this
keyword which is ``pyscaffold_keyword`` below. This is where we hook into
setuptools and apply the magic of setuptools_scm and pbr.
"""

from __future__ import division, print_function, absolute_import

from setuptools_scm.integration import find_files
from setuptools_scm.version import _warn_if_setuptools_outdated
from setuptools_scm import get_version
from setuptools_scm.utils import trace
from pbr.core import pbr as read_setup_cfg

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def version2str(version):
    if version.exact or not version.distance > 0:
        return version.format_with('{tag}')
    else:
        distance = version.distance
        version = str(version.tag)
        if '.dev' in version:
            version, tail = version.rsplit('.dev', 1)
            assert tail == '0', 'own dev numbers are unsupported'
        return '{}.post0.dev{}'.format(version, distance)


def local_version2str(version):
    if version.exact:
        if version.dirty:
            return version.format_with('+dirty')
        else:
            return ''
    else:
        if version.dirty:
            return version.format_with('+{node}.dirty')
        else:
            return version.format_with('+{node}')


def pyscaffold_keyword(dist, keyword, value):
    _warn_if_setuptools_outdated()
    if not value:
        return
    if value is True:
        read_setup_cfg(dist, keyword, value)
        try:
            dist.metadata.version = get_version(version_scheme=version2str,
                                                local_scheme=local_version2str)
        except Exception as e:
            trace('error', e)
