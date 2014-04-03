#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Setup file for setup_pyproject
"""

from __future__ import print_function, division, absolute_import

import os
import inspect
from distutils.cmd import Command

import setuptools
import versioneer
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

main_package = "pyscaffold"

versioneer.versionfile_source = os.path.join(main_package, '_version.py')
versioneer.versionfile_build = os.path.join(main_package, '_version.py')
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = main_package + '-'


def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
        from sphinx import apidoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run:\npip install sphinx")

        return NoSphinx

    class BuildSphinxDocs(BuildDoc):

        def run(self):
            output_dir = os.path.join(__location__, "docs/_rst")
            module_dir = os.path.join(__location__, main_package)
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

# Some help variables for setup()
version = versioneer.get_version()
docs_path = os.path.join(__location__, "docs")
docs_build_path = os.path.join(docs_path, "_build")
install_reqs_path = os.path.join(__location__, "requirements.txt")
install_reqs = get_install_requirements(install_reqs_path)
console_scripts = ['putup = pyscaffold.runner:run']
setup(name=main_package,
      version=version,
      url="http://blue-yonder.com/",
      description="Tool for easily putting up the scaffold for a "
                  "Python project",
      author="Florian Wilhelm",
      author_email="Florian.Wilhelm@blue-yonder.com",
      license="proprietary",
      long_description=read('README.txt'),
      platforms=["Linux"],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                   'Topic :: Scientific/Engineering',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Operating System :: Unix',
                   'Operating System :: MacOS',
                   'License :: Other/Proprietary License'],
      test_suite='tests',
      packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
      install_requires=install_reqs,
      cmdclass=cmdclass,
      extras_require={'docs': ['sphinx']},
      command_options={
          'docs': {'project': ('setup.py', main_package),
                   'version': ('setup.py', version.split('-', 1)[0]),
                   'release': ('setup.py', version),
                   'build_dir': ('setup.py', docs_build_path),
                   'config_dir': ('setup.py', docs_path),
                   'source_dir': ('setup.py', docs_path)}
      },
      entry_points={'console_scripts': console_scripts})
