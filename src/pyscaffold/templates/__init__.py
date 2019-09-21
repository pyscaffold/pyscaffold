# -*- coding: utf-8 -*-
"""
Templates for all files of a project's scaffold
"""

import os
import string
from pkg_resources import resource_string

from ..utils import get_setup_requires_version
from .. import __version__ as pyscaffold_version
from ..contrib.configupdater import ConfigUpdater


#: All available licences
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
    file_name = "{name}.template".format(name=name)
    data = resource_string(__name__, file_name)
    # we assure that line endings are converted to '\n' for all OS
    data = data.decode(encoding="utf-8").replace(os.linesep, '\n')
    return string.Template(data)


def setup_py(opts):
    """Template of setup.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("setup_py")
    return template.safe_substitute(opts)


def setup_cfg(opts):
    """Template of setup.cfg

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("setup_cfg")
    opts["setup_requires_str"] = get_setup_requires_version()
    cfg_str = template.substitute(opts)

    updater = ConfigUpdater()
    updater.read_string(cfg_str)

    # add `classifiers`
    (updater["metadata"]["platforms"].add_after
     .comment("Add here all kinds of additional classifiers as defined under")
     .comment("https://pypi.python.org/pypi?%3Aaction=list_classifiers")
     .option("classifiers"))
    updater["metadata"]["classifiers"].set_values(opts["classifiers"])

    # add `install_requires`
    setup_requires = updater["options"]["setup_requires"]
    if opts["requirements"]:
        setup_requires.add_after.option("install_requires")
        updater["options"]["install_requires"].set_values(opts["requirements"])
    else:
        (setup_requires.add_after
         .comment("Add here dependencies of your project "
                  "(semicolon/line-separated), e.g.")
         .comment("install_requires = numpy; scipy"))

    # fill [pyscaffold] section used for later updates
    pyscaffold = updater["pyscaffold"]
    pyscaffold["version"] = pyscaffold_version
    pyscaffold["package"] = opts["package"]
    if opts["cli_params"]["extensions"]:
        pyscaffold.set("extensions")
        pyscaffold["extensions"].set_values(opts["cli_params"]["extensions"])
        for extension, args in opts["cli_params"]["args"].items():
            pyscaffold[extension] = args

    return str(updater)


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
    reqs = "\n".join(opts["requirements"]) or "#"
    opts["requirements_str"] = reqs
    return template.substitute(opts)


def license(opts):
    """Template of LICENSE.txt

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template(licenses[opts["license"]])
    return template.substitute(opts)


def init(opts):
    """Template of __init__.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    if opts["package"] == opts["project"]:
        opts["distribution"] = "__name__"
    else:
        opts["distribution"] = "'{}'".format(opts["project"])
    template = get_template("__init__")
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


def isort_cfg(opts):
    """Template of .isort.cfg

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("isort_cfg")
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
