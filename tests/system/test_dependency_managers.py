import json
import os
from functools import partial
from os import environ
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from pyscaffold import __version__ as pyscaffold_version
from pyscaffold.api import create_project
from pyscaffold.extensions.venv import Venv

from .helpers import find_venv_bin, run

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


@pytest.mark.skipif(
    os.name == "nt", reason="pipenv fails due to colors (non-utf8) under Windows 10"
)
def test_pipenv_works_with_pyscaffold(tmpfolder, venv_path, venv_run):
    # Given a project is created with pyscaffold
    # and it has some dependencies in setup.cfg
    create_project(project_path="myproj", requirements=["appdirs"])

    if any(ch in pyscaffold_version for ch in ("b", "a", "pre", "rc")):
        flags = "--pre"
    else:
        flags = ""

    with tmpfolder.join("myproj").as_cwd():
        # When we install pipenv,
        venv_run("pip install -v pipenv")
        venv_run("pipenv --bare install certifi")
        # use it to proxy setup.cfg
        venv_run("pipenv --bare install {} -e .".format(flags))
        # and install things to the dev env,
        venv_run("pipenv --bare install --dev flake8")

        # Then it should be able to generate a Pipfile.lock
        venv_run("pipenv lock")
        assert Path("Pipfile.lock").exists()

        # with the correct dependencies
        with open("Pipfile.lock") as fp:
            content = json.load(fp)
            assert content["default"]["appdirs"]
            assert content["develop"]["flake8"]

        # and run things from inside pipenv's venv
        assert venv_path in venv_run("pipenv run which flake8")
        venv_run("pipenv --bare run flake8 src/myproj/skeleton.py")


def test_piptools_works_with_pyscaffold(tmpfolder, monkeypatch):
    venv_path = Path(str(tmpfolder), "myproj/.venv").resolve()
    find = partial(find_venv_bin, venv_path)
    # Given a project is created with pyscaffold
    # and it has some dependencies in setup.cfg
    create_project(project_path="myproj", extensions=[Venv()], requirements=["appdirs"])
    with tmpfolder.join("myproj").as_cwd():
        requirements_in = Path("requirements.in")
        # When we install pip-tools
        run(f"{find('pip')} install -v pip-tools certifi")
        # and write a requirements.in file that proxies setup.cfg
        # and install other things,
        requirements_in.write_text("-e file:.\nflake8")
        # Then we should be able to generate a requirements.txt
        run(find("pip-compile"))
        requirements_txt = Path("requirements.txt")
        assert requirements_txt.exists()
        # with the correct dependencies
        content = requirements_txt.read_text()
        assert "appdirs==" in content
        assert "flake8==" in content
        assert "file:." in content
        # install the dependencies
        # and run things from inside pipenv's venv
        pip_sync = find("pip-sync")
        try:
            # pip-tools have problems on windows inside a test env with relative paths
            run(pip_sync)
            run(f"{find('flake8')} src/myproj/skeleton.py")
        except CalledProcessError as ex:
            if "assert" in ex.output:
                pytest.skip(
                    "pip-tools tries to assert a path is absolute, which fails "
                    "inside test env for some OSs"
                )
            else:
                raise
