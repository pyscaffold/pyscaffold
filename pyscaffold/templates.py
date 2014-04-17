# -*- coding: utf-8 -*-
import os.path
from pkgutil import get_data

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def get_template(name):
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("data", file_name))
    return data.decode()


def get_setup():
    return get_template("setup")


def get_gitignore():
    return get_template("gitignore")


def get_sphinx_conf():
    return get_template("sphinx_conf")


def get_sphinx_index():
    return get_template("sphinx_index")


def get_versioneer():
    return get_template("versioneer")


def get_version():
    return get_template("_version")


def get_manifest_in():
    return get_template("manifest_in")


def get_sphinx_makefile():
    return get_template("sphinx_makefile")


def get_readme():
    return get_template("readme")


def get_authors():
    return get_template("authors")


def get_requirements():
    return get_template("requirements")


def get_copying():
    return get_template("copying")


def get_init():
    return get_template("__init__")


def get_coveragerc():
    return get_template("coveragerc")
