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

import os
from distutils.cmd import Command

from setuptools_scm import get_version
from setuptools_scm.utils import trace
from setuptools_scm.version import _warn_if_setuptools_outdated
from pbr.core import pbr as read_setup_cfg

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def version2str(version):
    """
    Creates a PEP440 version string

    :param version: version object as :obj:`setuptools_scm.version.ScmVersion`
    :return: version string
    """
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
    """
    Create the local part of a PEP440 version string

    :param version: version object as :obj:`setuptools_scm.version.ScmVersion`
    :return: local version string
    """
    if version.exact:
        return ''
    else:
        if version.dirty:
            return version.format_with('+{node}.dirty')
        else:
            return version.format_with('+{node}')


def deactivate_pbr_authors_changelog():
    """
    Deactivate automatic generation of AUTHORS and ChangeLog file

    This is an automatism of PBR and we rather keep track of our own
    AUTHORS.rst and CHANGES.rst files.
    """
    os.environ['SKIP_GENERATE_AUTHORS'] = "1"
    # This is commented only due to a bug in PBR,
    # see https://bugs.launchpad.net/pbr/+bug/1467440
    # os.environ['SKIP_WRITE_GIT_CHANGELOG'] = "1"


def build_cmd_docs():
    """
    Return Sphinx's BuildDoc if available otherwise a dummy command

    :return: command as :obj:`~distutils.cmd.Command`
    """
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx
    else:
        return BuildDoc


def pyscaffold_keyword(dist, keyword, value):
    """
    Handles the `use_pyscaffold` keyword of the setup(...) command

    :param dist: distribution object as :obj:`setuptools.dist`
    :param keyword: keyword argument = 'use_pyscaffold'
    :param value: value of the keyword argument
    """
    _warn_if_setuptools_outdated()
    if value is True:
        deactivate_pbr_authors_changelog()
        read_setup_cfg(dist, keyword, value)
        try:
            dist.metadata.version = get_version(version_scheme=version2str,
                                                local_scheme=local_version2str)
        except Exception as e:
            trace('error', e)
        # Adding doctest again since PBR seems to drop these
        dist.cmdclass['doctest'] = build_cmd_docs()
        dist.command_options['doctest'] = {'builder': ('setup.py', 'doctest')}
