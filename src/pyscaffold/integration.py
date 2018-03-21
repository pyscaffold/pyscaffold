# -*- coding: utf-8 -*-

"""
Integration part for hooking into distutils/setuptools

Rationale:
The ``use_pyscaffold`` keyword is unknown to setuptools' setup(...) command,
therefore the ``entry_points`` are checked for a function to handle this
keyword which is ``pyscaffold_keyword`` below. This is where we hook into
setuptools and apply the magic of setuptools_scm as well as other commands.
"""
from __future__ import division, print_function, absolute_import

import sys
from distutils.cmd import Command

from pyscaffold.contrib import ptr
from pyscaffold.contrib.setuptools_scm import get_version, discover
from pyscaffold.utils import check_setuptools_version
from pyscaffold.repo import get_git_root


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
            return version.format_with('+{node}.dirty')
        else:
            return version.format_with('+{node}')


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


class PyTest(ptr.PyTest):
    def run_tests(self):
        try:
            import pytest  # noqa
        except ImportError:
            raise RuntimeError("PyTest is not installed, run: "
                               "pip install pytest pytest-cov")
        super(PyTest, self).run_tests()
        sys.exit(self.result_code)


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
        matching_fallbacks = discover.iter_matching_entrypoints(
            '.', 'setuptools_scm.parse_scm_fallback')
        if any(matching_fallbacks):
            value.pop('root', None)
        dist.metadata.version = get_version(**value)
        dist.cmdclass['docs'] = build_cmd_docs()
        dist.cmdclass['doctest'] = build_cmd_docs()
        dist.command_options['doctest'] = {'builder': ('setup.py', 'doctest')}
        dist.cmdclass['test'] = PyTest
