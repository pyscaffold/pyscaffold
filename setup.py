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

import setuptools
from setuptools import setup
from setuptools.command.test import test as TestCommand

import versioneer

# For Python 2/3 compatibility, pity we can't use six.moves here
try:  # try Python 3 imports first
    import configparser
    from io import StringIO
except ImportError:  # then fall back to Python 2
    import ConfigParser as configparser
    from StringIO import StringIO

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

package = "pyscaffold"

# Versioneer configuration
versioneer.VCS = 'git'
versioneer.versionfile_source = os.path.join(package, '_version.py')
versioneer.versionfile_build = os.path.join(package, '_version.py')
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = package + '-'


class PyTest(TestCommand):
    user_options = [("cov=", None, "Run coverage"),
                    ("cov-report=", None, "Generate a coverage report"),
                    ("junitxml=", None, "Generate xml of test results")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.cov_report = None
        self.junitxml = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]
            if self.cov_report:
                self.cov.extend(["--cov-report", self.cov_report])
        if self.junitxml:
            self.junitxml = ["--junitxml", self.junitxml]

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
        if self.junitxml:
            params["args"] += self.junitxml
        errno = pytest.main(**params)
        sys.exit(errno)


def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx

    class BuildSphinxDocs(BuildDoc):

        def run(self):
            if self.builder == "doctest":
                import sphinx.ext.doctest as doctest
                # Capture the DocTestBuilder class in order to return the total
                # number of failures when exiting
                ref = capture_objs(doctest.DocTestBuilder)
                BuildDoc.run(self)
                errno = ref[-1].total_failures
                sys.exit(errno)
            else:
                BuildDoc.run(self)

    return BuildSphinxDocs


class ObjKeeper(type):
    instances = {}

    def __init__(cls, name, bases, dct):
        cls.instances[cls] = []

    def __call__(cls, *args, **kwargs):
        cls.instances[cls].append(super(ObjKeeper, cls).__call__(*args,
                                                                 **kwargs))
        return cls.instances[cls][-1]


def capture_objs(cls):
    from six import add_metaclass
    module = inspect.getmodule(cls)
    name = cls.__name__
    keeper_class = add_metaclass(ObjKeeper)(cls)
    setattr(module, name, keeper_class)
    cls = getattr(module, name)
    return keeper_class.instances[cls]


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.splitlines() if req != '']


def read(fname):
    return open(os.path.join(__location__, fname)).read()


def read_setup_cfg():
    config = configparser.SafeConfigParser(allow_no_value=True)
    config_file = StringIO(read(os.path.join(__location__, 'setup.cfg')))
    config.readfp(config_file)
    metadata = dict(config.items('metadata'))
    metadata['classifiers'] = [item.strip() for item
                               in metadata['classifiers'].split(',')]
    console_scripts = dict(config.items('console_scripts'))
    console_scripts = prepare_console_scripts(console_scripts)
    return metadata, console_scripts


def prepare_console_scripts(dct):
    return ['{cmd} = {func}'.format(cmd=k, func=v) for k, v in dct.items()]


def setup_package():
    # Assemble additional setup commands
    cmdclass = versioneer.get_cmdclass()
    cmdclass['docs'] = sphinx_builder()
    cmdclass['doctest'] = sphinx_builder()
    cmdclass['test'] = PyTest

    # Some helper variables
    version = versioneer.get_version()
    docs_path = os.path.join(__location__, "docs")
    docs_build_path = os.path.join(docs_path, "_build")
    install_reqs = get_install_requirements("requirements.txt")
    metadata, console_scripts = read_setup_cfg()

    command_options = {
        'docs': {'project': ('setup.py', package),
                 'version': ('setup.py', version.split('-', 1)[0]),
                 'release': ('setup.py', version),
                 'build_dir': ('setup.py', docs_build_path),
                 'config_dir': ('setup.py', docs_path),
                 'source_dir': ('setup.py', docs_path)},
        'doctest': {'project': ('setup.py', package),
                    'version': ('setup.py', version.split('-', 1)[0]),
                    'release': ('setup.py', version),
                    'build_dir': ('setup.py', docs_build_path),
                    'config_dir': ('setup.py', docs_path),
                    'source_dir': ('setup.py', docs_path),
                    'builder': ('setup.py', 'doctest')},
        'test': {'test_suite': ('setup.py', 'tests'),
                 'cov': ('setup.py', package)}}

    setup(name=package,
          version=version,
          url=metadata['url'],
          description=metadata['description'],
          author=metadata['author'],
          author_email=metadata['author_email'],
          license=metadata['license'],
          long_description=read('README.rst'),
          classifiers=metadata['classifiers'],
          test_suite='tests',
          packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
          install_requires=install_reqs,
          setup_requires=['six'],
          cmdclass=cmdclass,
          tests_require=['pytest-cov', 'pytest'],
          include_package_data=True,
          package_data={package: ['data/*']},
          command_options=command_options,
          entry_points={'console_scripts': console_scripts})

if __name__ == "__main__":
    setup_package()
