#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Setup file of PyScaffold
"""

import os
import sys
import inspect
from distutils.cmd import Command

import versioneer
import setuptools
from setuptools import setup
from setuptools.command.test import test as TestCommand

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

MAIN_PACKAGE = "pyscaffold"
DESCRIPTION = "Tool for easily putting up the scaffold of a Python project"
LICENSE = "new BSD"
URL = "https://github.com/blue-yonder/pyscaffold"
AUTHOR = "Florian Wilhelm"
EMAIL = "Florian.Wilhelm@blue-yonder.com"

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = ['Development Status :: 4 - Beta',
               'Programming Language :: Python',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: BSD License',
               'Operating System :: POSIX :: Linux',
               'Topic :: Utilities']

console_scripts = ['putup = pyscaffold.runner:run']

# Versioneer configuration
versioneer.versionfile_source = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.versionfile_build = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = MAIN_PACKAGE + '-'


class PyTest(TestCommand):
    user_options = [("cov=", None, "Run coverage")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov is not None:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]

    def run_tests(self):
        try:
            import pytest
        except:
            raise RuntimeError("py.test is not installed, "
                               "run: pip install pytest")
        params = {"args": self.test_args}
        if self.cov:
            params["args"] += self.cov
            params["plugins"] = ["cov"]
        errno = pytest.main(**params)
        sys.exit(errno)


def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
        from sphinx import apidoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx

    class BuildSphinxDocs(BuildDoc):

        def run(self):
            output_dir = os.path.join(__location__, "docs/_rst")
            module_dir = os.path.join(__location__, MAIN_PACKAGE)
            cmd_line_template = "sphinx-apidoc -f -o {outputdir} {moduledir}"
            cmd_line = cmd_line_template.format(outputdir=output_dir,
                                                moduledir=module_dir)
            apidoc.main(cmd_line.split(" "))
            BuildDoc.run(self)

    return BuildSphinxDocs


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split("\n") if req != '']


def read(fname):
    return open(os.path.join(__location__, fname)).read()


# Assemble additional setup commands
cmdclass = versioneer.get_cmdclass()
cmdclass['docs'] = sphinx_builder()
cmdclass['doctest'] = sphinx_builder()
cmdclass['test'] = PyTest

# Some help variables for setup()
version = versioneer.get_version()
docs_path = os.path.join(__location__, "docs")
docs_build_path = os.path.join(docs_path, "_build")
install_reqs = get_install_requirements("requirements.txt")


def setup_package():
    setup(name=MAIN_PACKAGE,
          version=version,
          url=URL,
          description=DESCRIPTION,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          long_description=read('README.rst'),
          classifiers=classifiers,
          test_suite='tests',
          packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
          install_requires=install_reqs,
          cmdclass=cmdclass,
          tests_require=['pytest', 'pytest-cov'],
          extras_require={'docs': ['sphinx'],
                          'nosetests': ['nose']},
          command_options={
              'docs': {'project': ('setup.py', MAIN_PACKAGE),
                       'version': ('setup.py', version.split('-', 1)[0]),
                       'release': ('setup.py', version),
                       'build_dir': ('setup.py', docs_build_path),
                       'config_dir': ('setup.py', docs_path),
                       'source_dir': ('setup.py', docs_path)},
              'doctest': {'project': ('setup.py', MAIN_PACKAGE),
                          'version': ('setup.py', version.split('-', 1)[0]),
                          'release': ('setup.py', version),
                          'build_dir': ('setup.py', docs_build_path),
                          'config_dir': ('setup.py', docs_path),
                          'source_dir': ('setup.py', docs_path),
                          'builder': ('setup.py', 'doctest')},
              'test': {'test_suite': ('setup.py', 'tests'),
                       'cov': ('setup.py', 'pyscaffold')}
          },
          include_package_data=True,
          package_data={MAIN_PACKAGE: ['data/*']},
          entry_points={'console_scripts': console_scripts})

if __name__ == "__main__":
    setup_package()