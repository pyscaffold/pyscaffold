# -*- coding: utf-8 -*-
"""
Templates for all files of a project's scaffold
"""
from __future__ import absolute_import, print_function

import os.path
import string
from pkgutil import get_data

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
    data = get_data(pkg_name, os.path.join("templates", file_name))
    return string.Template(data.decode(encoding='utf8'))


def setup_py(opts):
    """
    Template of setup.py

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("setup_py")
    return template.safe_substitute(opts)


def setup_cfg(opts):
    """
    Template of setup.cfg

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("setup_cfg")
    return template.substitute(opts)


def gitignore(opts):
    """
    Template of .gitignore

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("gitignore")
    return template.substitute(opts)


def gitignore_empty(opts):
    """
    Template of empty .gitignore

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("gitignore_empty")
    return template.substitute(opts)


def sphinx_conf(opts):
    """
    Template of conf.py

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_conf")
    return template.substitute(opts)


def sphinx_index(opts):
    """
    Template of index.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_index")
    return template.substitute(opts)


def sphinx_license(opts):
    """
    Template of license.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_license")
    return template.substitute(opts)


def sphinx_authors(opts):
    """
    Template of authors.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_authors")
    return template.substitute(opts)


def sphinx_changes(opts):
    """
    Template of changes.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_changes")
    return template.substitute(opts)


def sphinx_makefile(opts):
    """
    Template of Sphinx's Makefile

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("sphinx_makefile")
    return template.safe_substitute(opts)


def readme(opts):
    """
    Template of README.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("readme")
    return template.substitute(opts)


def authors(opts):
    """
    Template of AUTHORS.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("authors")
    return template.substitute(opts)


def requirements(opts):
    """
    Template of requirements.txt

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("requirements")
    return template.substitute(
        requirements_str=',\n'.join(opts['requirements']), **opts)


def test_requirements(opts):
    """
    Template of test-requirements.txt

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("test_requirements")
    return template.substitute(opts)


def license(opts):
    """
    Template of LICENSE.txt

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template(licenses[opts['license']])
    return template.substitute(opts)


def init(opts):
    """
    Template of __init__.py

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("__init__")
    return template.substitute(opts)


def coveragerc(opts):
    """
    Template of .coveragerc

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("coveragerc")
    return template.substitute(opts)


def tox(opts):
    """
    Template of tox.ini

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("tox_ini")
    return template.substitute(opts)


def travis(opts):
    """
    Template of .travis.yml

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("travis")
    return template.safe_substitute(opts)


def travis_install(opts):
    """
    Template of travis_install.sh

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("travis_install")
    return template.safe_substitute(opts)


def pre_commit_config(opts):
    """
    Template of .pre-commit-config.yaml

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("pre-commit-config")
    return template.safe_substitute(opts)


def namespace(opts):
    """
    Template of __init__.py defining a namespace package

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("namespace")
    return template.substitute(opts)


def skeleton(opts):
    """
    Template of skeleton.py defining a basic console script

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("skeleton")
    return template.substitute(opts)


def test_skeleton(opts):
    """
    Template of unittest for skeleton.py

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("test_skeleton")
    return template.substitute(opts)


def changes(opts):
    """
    Template of CHANGES.rst

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("changes")
    return template.substitute(opts)


def conftest_py(opts):
    """
    Template of conftest.py

    :param opts: mapping parameters as dictionary
    :return: file content as string
    """
    template = get_template("conftest_py")
    return template.substitute(opts)
