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
from distutils.filelist import FileList

import setuptools
from setuptools import setup

# For Python 2/3 compatibility, pity we can't use six.moves here
try:  # try Python 3 imports first
    import configparser
except ImportError:  # then fall back to Python 2
    import ConfigParser as configparser

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

# determine root package and package path if namespace package is used
package = "pyscaffold"
namespace = []
root_pkg = namespace[0] if namespace else package
if namespace:
    pkg_path = os.path.join(*namespace[-1].split('.') + [package])
else:
    pkg_path = package


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
    docs_path = os.path.join(__location__, "docs")
    docs_build_path = os.path.join(docs_path, "_build")
    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []

    command_options = {
        'docs': {'project': ('setup.py', package),
                 'build_dir': ('setup.py', docs_build_path),
                 'config_dir': ('setup.py', docs_path),
                 'source_dir': ('setup.py', docs_path)},
        'doctest': {'project': ('setup.py', package),
                    'build_dir': ('setup.py', docs_build_path),
                    'config_dir': ('setup.py', docs_path),
                    'source_dir': ('setup.py', docs_path),
                    'builder': ('setup.py', 'doctest')}
    }

    setup(setup_requires=['six'] + pytest_runner,
          tests_require=['pytest-cov', 'pytest'],
          cmdclass={'docs': build_cmd_docs(), 'doctest': build_cmd_docs()},
          command_options=command_options,
          use_pyscaffold=True,
          # Need to pass this since hook for setup.cfg does not exist yet
          entry_points="""
             [distutils.setup_keywords]
             use_pyscaffold = pyscaffold.integration:pyscaffold_keyword"""
          )


if __name__ == "__main__":
    setup_package()
