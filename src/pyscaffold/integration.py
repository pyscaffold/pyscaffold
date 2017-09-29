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

from pyscaffold.contrib import pbr_read_setup_cfg, scm_get_version
from pyscaffold.utils import check_setuptools_version
from pyscaffold.repo import get_git_root
from pyscaffold.pytest_runner import PyTest

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def version2str(version):
    """Creates a PEP440 version string

    Args:
        version (:obj:`setuptools_scm.version.ScmVersion`): version object

    Returns:
        str: version string
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
    """Create the local part of a PEP440 version string

    Args:
        version (:obj:`setuptools_scm.version.ScmVersion`): version object

    Returns:
        str: local version
    """
    if version.exact:
        return ''
    else:
        if version.dirty:
            return version.format_with('+n{node}.dirty')
        else:
            return version.format_with('+n{node}')


def deactivate_pbr_authors_changelog():
    """Deactivate automatic generation of AUTHORS and ChangeLog file

    This is an automatism of pbr and we rather keep track of our own
    AUTHORS.rst and CHANGES.rst files.
    """
    os.environ['SKIP_GENERATE_AUTHORS'] = "1"
    os.environ['SKIP_WRITE_GIT_CHANGELOG'] = "1"


def build_cmd_docs():
    """Return Sphinx's BuildDoc if available otherwise a dummy command

    Returns:
        :obj:`~distutils.cmd.Command`: command object
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
    """Handles the `use_pyscaffold` keyword of the setup(...) command

    Args:
        dist (:obj:`setuptools.dist`): distribution object as
        keyword (str): keyword argument = 'use_pyscaffold'
        value: value of the keyword argument
    """
    check_setuptools_version()
    if value:
        # If value is a dictionary we keep it otherwise use for configuration
        value = value if isinstance(value, dict) else dict()
        value.setdefault('root', get_git_root(default='.'))
        value.setdefault('version_scheme', version2str)
        value.setdefault('local_scheme', local_version2str)
        if os.path.exists('PKG-INFO'):
            value.pop('root', None)
        command_options = dist.command_options.copy()
        cmdclass = dist.cmdclass.copy()
        deactivate_pbr_authors_changelog()
        pbr_read_setup_cfg(dist, keyword, True)
        dist.metadata.version = scm_get_version(**value)
        # Adding old command classes and options since pbr seems to drop these
        dist.cmdclass['doctest'] = build_cmd_docs()
        dist.command_options['doctest'] = {'builder': ('setup.py', 'doctest')}
        dist.cmdclass['test'] = PyTest
        dist.cmdclass.update(cmdclass)
        dist.cmdclass.update(command_options)
