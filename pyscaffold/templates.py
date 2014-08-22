# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os.path
import string
from pkgutil import get_data

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def get_template(name):
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("data", file_name))
    return string.Template(data.decode())


def setup(args):
    template = get_template("setup")
    return template.substitute(vars(args))


def gitignore(args):
    template = get_template("gitignore")
    return template.substitute(vars(args))


def gitignore_empty(args):
    template = get_template("gitignore_empty")
    return template.substitute(vars(args))


def sphinx_conf(args):
    template = get_template("sphinx_conf")
    return template.substitute(vars(args))


def sphinx_index(args):
    template = get_template("sphinx_index")
    return template.substitute(vars(args))


def sphinx_license(args):
    template = get_template("sphinx_license")
    return template.substitute(vars(args))


def versioneer(args):
    template = get_template("versioneer")
    return template.safe_substitute(vars(args))


def version(args):
    template = get_template("_version")
    return template.safe_substitute(vars(args))


def manifest_in(args):
    template = get_template("manifest_in")
    return template.substitute(vars(args))


def sphinx_makefile(args):
    template = get_template("sphinx_makefile")
    return template.safe_substitute(vars(args))


def readme(args):
    template = get_template("readme")
    return template.substitute(vars(args))


def authors(args):
    template = get_template("authors")
    return template.substitute(vars(args))


def requirements(args):
    template = get_template("requirements")
    return template.substitute(vars(args))


def copying(args):
    template = get_template("copying")
    return template.substitute(vars(args))


def init(args):
    template = get_template("__init__")
    return template.substitute(vars(args))


def coveragerc(args):
    template = get_template("coveragerc")
    return template.substitute(vars(args))


def travis(args):
    template = get_template("travis")
    return template.safe_substitute(vars(args))


def travis_install(args):
    template = get_template("travis_install")
    return template.safe_substitute(vars(args))
