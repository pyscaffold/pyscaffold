#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    This file was generated with PyScaffold, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    http://pyscaffold.readthedocs.org/
"""

import inspect
import os
import sys
from distutils.cmd import Command

from setuptools import setup, Distribution

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"
__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


def build_cmd_docs():
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


def setup_package():
    # Install our dependencies directly since we need them now
    dist = Distribution()
    dist.fetch_build_eggs(['six', 'setuptools_scm>=1.5,<1.6', 'pbr>=1.2,<1.3'])
    from pbr.util import cfg_to_args

    docs_path = os.path.join(__location__, 'docs')
    docs_build_path = os.path.join(docs_path, '_build')
    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    command_options = {
        'docs': {'build_dir': ('setup.py', docs_build_path),
                 'config_dir': ('setup.py', docs_path),
                 'source_dir': ('setup.py', docs_path)},
        'doctest': {'build_dir': ('setup.py', docs_build_path),
                    'config_dir': ('setup.py', docs_path),
                    'source_dir': ('setup.py', docs_path),
                    'builder': ('setup.py', 'doctest')}
    }
    kwargs = cfg_to_args()
    kwargs['setup_requires'] = ['six'] + pytest_runner
    kwargs['tests_require'] = ['pytest-cov', 'pytest']
    kwargs['cmdclass'] = {'docs': build_cmd_docs(),
                          'doctest': build_cmd_docs()}
    kwargs['command_options'] = command_options
    setup(**kwargs)


if __name__ == '__main__':
    setup_package()
