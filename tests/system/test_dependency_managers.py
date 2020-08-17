# -*- coding: utf-8 -*-
import json
import os
from os import environ
from os.path import exists

import pytest

from pyscaffold import __version__ as pyscaffold_version
from pyscaffold.api import create_project

pytestmark = [pytest.mark.slow, pytest.mark.system]


@pytest.fixture(autouse=True)
def dont_load_dotenv():
    """pytest-virtualenv creates a `.env` directory by default, but `.env`
    entries in the file system are loaded by Pipenv as dotenv files.

    To prevent errors for happening we have to disable this feature.

    Additionally, it seems that env vars have to be changed before using
    venv, so an autouse fixture is required (cannot put this part in the
    beginning of the test function.
    """
    environ["PIPENV_DONT_LOAD_ENV"] = "1"


@pytest.fixture(autouse=True)
def cwd(tmpdir):
    """Guarantee a blank folder as workspace"""

    with tmpdir.as_cwd():
        yield tmpdir


@pytest.mark.skipif(
    os.name == "nt", reason="pipenv fails due to colors (non-utf8) under Windows 10"
)
def test_pipenv_works_with_pyscaffold(cwd, venv_path, venv_run):
    # Given a project is created with pyscaffold
    # and it has some dependencies in setup.cfg
    create_project(project="myproj", requirements=["appdirs"])

    if any(ch in pyscaffold_version for ch in ("b", "a", "pre", "rc")):
        flags = "--pre"
    else:
        flags = ""

    with cwd.join("myproj").as_cwd():
        # When we install pipenv,
        venv_run("pip install -v pipenv")
        venv_run("pipenv --bare install certifi")
        # use it to proxy setup.cfg
        venv_run("pipenv --bare install {} -e .".format(flags))
        # and install things to the dev env,
        venv_run("pipenv --bare install --dev flake8")

        # Then it should be able to generate a Pipfile.lock
        venv_run("pipenv lock")
        assert exists("Pipfile.lock")

        # with the correct dependencies
        with open("Pipfile.lock") as fp:
            content = json.load(fp)
            assert content["default"]["appdirs"]
            assert content["develop"]["flake8"]

        # and run things from inside pipenv's venv
        assert venv_path in venv_run("pipenv run which flake8")
        venv_run("pipenv --bare run flake8 src/myproj/skeleton.py")
