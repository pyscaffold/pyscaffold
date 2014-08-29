# -*- coding: utf-8 -*-
"""
Templates for all files of the project's scaffold
"""
from __future__ import print_function, absolute_import

import os.path
import string
from pkgutil import get_data

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def get_template(name):
    """
    Retrieve the template by name

    :param name: name of template
    :return: template as :obj:`string.Template`
    """
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("data", file_name))
    return string.Template(data.decode())


def setup(args):
    """
    Template of setup.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("setup")
    return template.substitute(vars(args))


def gitignore(args):
    """
    Template of .gitignore

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("gitignore")
    return template.substitute(vars(args))


def gitignore_empty(args):
    """
    Template of empty .gitignore

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("gitignore_empty")
    return template.substitute(vars(args))


def sphinx_conf(args):
    """
    Template of conf.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_conf")
    return template.substitute(vars(args))


def sphinx_index(args):
    """
    Template of index.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_index")
    return template.substitute(vars(args))


def sphinx_license(args):
    """
    Template of license.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_license")
    return template.substitute(vars(args))


def versioneer(args):
    """
    Template of versioneer.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("versioneer")
    return template.safe_substitute(vars(args))


def version(args):
    """
    Template of _version.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("_version")
    return template.safe_substitute(vars(args))


def manifest_in(args):
    """
    Template of MANIFEST.in

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("manifest_in")
    return template.substitute(vars(args))


def sphinx_makefile(args):
    """
    Template of Sphinx's Makefile

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_makefile")
    return template.safe_substitute(vars(args))


def readme(args):
    """
    Template of README.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("readme")
    return template.substitute(vars(args))


def authors(args):
    """
    Template of AUTHORS.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("authors")
    return template.substitute(vars(args))


def requirements(args):
    """
    Template of requirements.txt

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("requirements")
    return template.substitute(vars(args))


def copying(args):
    """
    Template of COPYING

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("copying")
    return template.substitute(vars(args))


def init(args):
    """
    Template of __init__.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("__init__")
    return template.substitute(vars(args))


def coveragerc(args):
    """
    Template of .coveragerc

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("coveragerc")
    return template.substitute(vars(args))


def travis(args):
    """
    Template of .travis.yml

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("travis")
    return template.safe_substitute(vars(args))


def travis_install(args):
    """
    Template of travis_install.sh

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("travis_install")
    return template.safe_substitute(vars(args))
