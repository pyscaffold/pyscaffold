# -*- coding: utf-8 -*-
"""
Templates for all files of a project's scaffold
"""
from __future__ import absolute_import, print_function

import os.path
import string
from pkgutil import get_data

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
    """Retrieve the template by name

    Args:
        name: name of template

    Returns:
        :obj:`string.Template`: template
    """
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("templates", file_name))
    return string.Template(data.decode(encoding='utf8'))


def setup_py(opts):
    """Template of setup.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("setup_py")
    return template.safe_substitute(opts)


def _add_line(key, value, first_line=False):
    txt = '{} = {}'.format(key, value)
    if first_line:
        return txt
    else:
        return '\n' + txt


def _add_list(lst, indent=4*' ', sep='\n'):
    return sep.join([indent + elem for elem in lst])


def setup_cfg(opts):
    """Template of setup.cfg

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    from ..utils import list2str
    template = get_template("setup_cfg")
    opts['classifiers_str'] = list2str(
        opts['classifiers'],
        indent=4,
        brackets=False,
        quotes=False,
        sep='')
    opts['requirements_str'] = '; '.join(opts['requirements'])
    # [pyscaffold] section used for later updates
    opts['pyscaffold'] = _add_line('version', opts['version'], first_line=True)
    opts['pyscaffold'] += _add_line('package', opts['package'])
    if opts['cli_params']['extensions']:
        opts['pyscaffold'] += '\nextensions =\n'
        opts['pyscaffold'] += _add_list(opts['cli_params']['extensions'])
        for extension, args in opts['cli_params']['args'].items():
            opts['pyscaffold'] += _add_line(extension, args)

    return template.substitute(opts)


def gitignore(opts):
    """Template of .gitignore

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("gitignore")
    return template.substitute(opts)


def gitignore_empty(opts):
    """Template of empty .gitignore

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("gitignore_empty")
    return template.substitute(opts)


def sphinx_conf(opts):
    """Template of conf.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_conf")
    return template.substitute(opts)


def sphinx_index(opts):
    """Template of index.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_index")
    return template.substitute(opts)


def sphinx_license(opts):
    """Template of license.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_license")
    return template.substitute(opts)


def sphinx_authors(opts):
    """Template of authors.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_authors")
    return template.substitute(opts)


def sphinx_changelog(opts):
    """Template of changelog.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_changelog")
    return template.substitute(opts)


def sphinx_makefile(opts):
    """Template of Sphinx's Makefile

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("sphinx_makefile")
    return template.safe_substitute(opts)


def readme(opts):
    """Template of README.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("readme")
    return template.substitute(opts)


def authors(opts):
    """Template of AUTHORS.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("authors")
    return template.substitute(opts)


def requirements(opts):
    """Template of requirements.txt

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("requirements")
    opts['requirements_str'] = '\n'.join(opts['requirements'])
    return template.substitute(opts)


def license(opts):
    """Template of LICENSE.txt

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template(licenses[opts['license']])
    return template.substitute(opts)


def init(opts):
    """Template of __init__.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    if opts['package'] == opts['project']:
        opts['distribution'] = '__name__'
    else:
        opts['distribution'] = "'{}'".format(opts['project'])
    template = get_template('__init__')
    return template.substitute(opts)


def coveragerc(opts):
    """Template of .coveragerc

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("coveragerc")
    return template.substitute(opts)


def tox(opts):
    """Template of tox.ini

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("tox_ini")
    return template.substitute(opts)


def travis(opts):
    """Template of .travis.yml

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("travis")
    return template.safe_substitute(opts)


def travis_install(opts):
    """Template of travis_install.sh

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("travis_install")
    return template.safe_substitute(opts)


def gitlab_ci(opts):
    """Template of .gitlab-ci.yml

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("gitlab_ci")
    return template.safe_substitute(opts)


def pre_commit_config(opts):
    """Template of .pre-commit-config.yaml

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("pre-commit-config")
    return template.safe_substitute(opts)


def namespace(opts):
    """Template of __init__.py defining a namespace package

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("namespace")
    return template.substitute(opts)


def skeleton(opts):
    """Template of skeleton.py defining a basic console script

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("skeleton")
    return template.substitute(opts)


def test_skeleton(opts):
    """Template of unittest for skeleton.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("test_skeleton")
    return template.substitute(opts)


def changelog(opts):
    """Template of CHANGELOG.rst

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("changelog")
    return template.substitute(opts)


def conftest_py(opts):
    """Template of conftest.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("conftest_py")
    return template.substitute(opts)
