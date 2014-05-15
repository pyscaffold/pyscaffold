#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    This file was generated with PyScaffold, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    https://github.com/blue-yonder/pyscaffold
"""

import os
import sys
import inspect
from distutils.cmd import Command

import versioneer
import setuptools
from setuptools.command.test import test as TestCommand
from setuptools import setup


__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

# Change these settings according to your needs
MAIN_PACKAGE = "pyscaffold"
DESCRIPTION = "Tool for easily putting up the scaffold of a Python project"
LICENSE = "new BSD"
URL = "https://github.com/blue-yonder/pyscaffold"
AUTHOR = "Florian Wilhelm"
EMAIL = "Florian.Wilhelm@blue-yonder.com"

COVERAGE_XML = False
COVERAGE_HTML = False
JUNIT_XML = False

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.2',
               'Programming Language :: Python :: 3.3',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: BSD License',
               'Operating System :: POSIX :: Linux',
               'Topic :: Utilities']

# Add here console scripts like ['hello_world = pyscaffold.module:function']
CONSOLE_SCRIPTS = ['putup = pyscaffold.runner:run']

# Versioneer configuration
versioneer.versionfile_source = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.versionfile_build = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = MAIN_PACKAGE + '-'


class PyTest(TestCommand):
    user_options = [("cov=", None, "Run coverage"),
                    ("cov-xml=", None, "Generate junit xml report"),
                    ("cov-html=", None, "Generate junit html report"),
                    ("junitxml=", None, "Generate xml of test results")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.cov_xml = False
        self.cov_html = False
        self.junitxml = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov is not None:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]
            if self.cov_xml:
                self.cov.extend(["--cov-report", "xml"])
            if self.cov_html:
                self.cov.extend(["--cov-report", "html"])
        if self.junitxml is not None:
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
            import sphinx.ext.doctest as doctest
            output_dir = os.path.join(__location__, "docs/_rst")
            module_dir = os.path.join(__location__, MAIN_PACKAGE)
            cmd_line_template = "sphinx-apidoc -f -o {outputdir} {moduledir}"
            cmd_line = cmd_line_template.format(outputdir=output_dir,
                                                moduledir=module_dir)
            apidoc.main(cmd_line.split(" "))
            if self.builder == "doctest":
                # Capture the DocTestBuilder class in order to return the total
                # number of failures when exiting
                ref = capture_objs(doctest.DocTestBuilder)
                BuildDoc.run(self)
                errno = ref[-1].total_failures
                sys.exit(errno)
            else:
                BuildDoc.run(self)

    return BuildSphinxDocs


# Taken from six, Copyright (c) 2010-2014 Benjamin Peterson, MIT License
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


class ObjKeeper(type):
    instances = {}

    def __init__(cls, name, bases, dct):
        cls.instances[cls] = []

    def __call__(cls, *args, **kwargs):
        cls.instances[cls].append(super(ObjKeeper, cls).__call__(*args,
                                                                 **kwargs))
        return cls.instances[cls][-1]


def capture_objs(cls):
    module = inspect.getmodule(cls)
    name = cls.__name__
    keeper_class = add_metaclass(ObjKeeper)(cls)
    setattr(module, name, keeper_class)
    cls = getattr(module, name)
    return keeper_class.instances[cls]


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split("\\n") if req != '']


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
    command_options = {
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
                 'cov': ('setup.py', 'pyscaffold')}}
    if JUNIT_XML:
        command_options['test']['junitxml'] = ('setup.py', 'junit.xml')
    if COVERAGE_XML:
        command_options['test']['cov_xml'] = ('setup.py', True)
    if COVERAGE_HTML:
        command_options['test']['cov_html'] = ('setup.py', True)

    setup(name=MAIN_PACKAGE,
          version=version,
          url=URL,
          description=DESCRIPTION,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          long_description=read('README.rst'),
          classifiers=CLASSIFIERS,
          test_suite='tests',
          packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
          install_requires=install_reqs,
          cmdclass=cmdclass,
          tests_require=['pytest-cov', 'pytest'],
          include_package_data=True,
          package_data={MAIN_PACKAGE: ['data/*']},
          command_options=command_options,
          entry_points={'console_scripts': CONSOLE_SCRIPTS})

if __name__ == "__main__":
    setup_package()
