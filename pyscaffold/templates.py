# -*- coding: utf-8 -*-
"""
Templates for all files of a project's scaffold
"""
from __future__ import absolute_import, print_function

import os.path
import string
from operator import itemgetter
from pkgutil import get_data

from .utils import levenshtein, safe_set

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"

licenses = {"affero": "license_affero_3.0",
            "apache": "license_apache",
            "artistic": "license_artistic_2.0",
            "cc0": "license_cc0_1.0",
            "eclipse": "license_eclipse_1.0",
            "gpl2": "license_gpl_2.0",
            "gpl3": "license_gpl_3.0",
            "isc": "license_isc",
            "lgpl2": "license_lgpl_2.1",
            "lgpl3": "license_lgpl_3.0",
            "mit": "license_mit",
            "mozilla": "license_mozilla",
            "new-bsd": "license_new_bsd",
            "none": "license_none",
            "proprietary": "license_none",
            "public-domain": "license_public_domain",
            "simple-bsd": "license_simplified_bsd"}


def get_template(name):
    """
    Retrieve the template by name

    :param name: name of template
    :return: template as :obj:`string.Template`
    """
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("data", file_name))
    return string.Template(data.decode(encoding='utf8'))


def setup_py(args):
    """
    Template of setup.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("setup_py")
    return template.safe_substitute(vars(args))


def setup_cfg(args):
    """
    Template of setup.cfg

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("setup_cfg")
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


def sphinx_authors(args):
    """
    Template of authors.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_authors")
    return template.substitute(vars(args))


def sphinx_changes(args):
    """
    Template of changes.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("sphinx_changes")
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
    safe_set(args, 'requirements_str', ',\n'.join(args.requirements))
    return template.substitute(vars(args))


def license(args):
    """
    Template of LICENSE.txt

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template(licenses[args.license])
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


def tox(args):
    """
    Template of tox.ini

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("tox_ini")
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


def pre_commit_config(args):
    """
    Template of .pre-commit-config.yaml

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("pre-commit-config")
    return template.safe_substitute(vars(args))


def best_fit_license(txt):
    """
    Finds proper license name for the license defined in txt

    :param txt: license name as string
    :return: license name as string
    """
    ratings = {lic: levenshtein(txt, lic.lower()) for lic in licenses}
    return min(ratings.items(), key=itemgetter(1))[0]


def namespace(args):
    """
    Template of __init__.py defining a namespace package

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("namespace")
    return template.substitute(vars(args))


def skeleton(args):
    """
    Template of skeleton.py defining a basic console script

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("skeleton")
    return template.substitute(vars(args))


def changes(args):
    """
    Template of CHANGES.rst

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("changes")
    return template.substitute(vars(args))


def conftest_py(args):
    """
    Template of conftest.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: file content as string
    """
    template = get_template("conftest_py")
    return template.substitute(vars(args))
