# -*- coding: utf-8 -*-
template = '''\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import inspect
from distutils.cmd import Command

import setuptools
import versioneer
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

# Change these according to your needs
MAIN_PACKAGE = "${package}"
DESCRIPTION = "ADD A DESCRIPTION HERE"
LICENSE = "ADD A LICENSE HERE"
URL = "http://www.${host}"
AUTHOR = "${author}"
EMAIL = "${email}"

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = ['Development Status :: 4 - Beta',
               'Programming Language :: Python']

# Add here console scripts like ['hello_world = ${package}.module:function']
console_scripts = []

# Versioneer configuration
versioneer.versionfile_source = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.versionfile_build = os.path.join(MAIN_PACKAGE, '_version.py')
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = MAIN_PACKAGE + '-'


def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
        from sphinx import apidoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run:\\npip install sphinx")

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
    return [req for req in content.split("\\n") if req != '']


def read(fname):
    return open(os.path.join(__location__, fname)).read()


# Assemble additional setup commands
cmdclass = versioneer.get_cmdclass()
cmdclass['docs'] = sphinx_builder()
cmdclass['doctest'] = sphinx_builder()

# Some help variables for setup()
version = versioneer.get_version()
docs_path = os.path.join(__location__, "docs")
docs_build_path = os.path.join(docs_path, "_build")
install_reqs = get_install_requirements("requirements.txt")

setup(name=MAIN_PACKAGE,
      version=version,
      url=URL,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      long_description=read('README.txt'),
      classifiers=classifiers,
      test_suite='tests',
      packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
      install_requires=install_reqs,
      cmdclass=cmdclass,
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
          'nosetests': {'with_coverage': ('setup.py', True),
                        'cover_html': ('setup.py', True),
                        'cover_package': ('setup.py', MAIN_PACKAGE)}
      },
      entry_points={'console_scripts': console_scripts})
'''
