# -*- coding: utf-8 -*-
import inspect

from . import setup
from . import gitignore
from . import sphinx_conf
from . import sphinx_index
from . import sphinx_makefile
from . import versioneer
from . import _version
from . import manifest_in
from . import readme
from . import authors


def get_setup():
    return setup.template


def get_gitignore():
    return gitignore.template


def get_sphinx_conf():
    return sphinx_conf.template


def get_sphinx_index():
    return sphinx_index.template


def get_versioneer():
    return inspect.getsource(versioneer)


def get_version():
    return _version.template


def get_manifest_in():
    return manifest_in.template


def get_sphinx_makefile():
    return sphinx_makefile.template


def get_readme():
    return readme.template


def get_authors():
    return authors.template