# -*- coding: utf-8 -*-
import json
from os import environ
from os.path import exists

import pytest

from pyscaffold.api import create_project

from . import venv_is_globally_available

pytestmark = [
    pytest.mark.slow,
    pytest.mark.system,
    pytest.mark.skipif(
        not venv_is_globally_available(),
        reason="python3 or venv module not found - tests require isolation",
    ),
]


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


# TODO: Fix this test... For some reason PIPENV fails to install
@pytest.mark.xfail
def test_pipenv_works_with_pyscaffold(cwd, venv):
    # Given a project is create with pyscaffold
    # and it have some dependencies in setup.cfg
    create_project(project_path="myproj", requirements=["appdirs"])
    with cwd.join("myproj").as_cwd():
        # TODO: Remove workaround https://github.com/pypa/pipenv/issues/2924
        # venv.pip('install -U pip==18.0')
        # When we install pipenv,
        venv.pip("install -v pipenv")
        # use it to proxy setup.cfg
        venv.run("pipenv install -e .")
        # and install things to the dev env,
        venv.run("pipenv install --dev flake8")

        # Then it should be able to generate a Pipfile.lock
        venv.run("pipenv lock")
        assert exists("Pipfile.lock")

        # with the correct dependencies
        with open("Pipfile.lock") as fp:
            content = json.load(fp)
            assert content["default"]["appdirs"]
            assert content["develop"]["flake8"]

        # and run things from inside pipenv's venv
        assert str(venv.path) in venv.run("pipenv run which flake8")
        venv.run("pipenv run flake8 src/myproj/skeleton.py")
