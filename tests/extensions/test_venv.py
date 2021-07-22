from argparse import ArgumentError
from itertools import product
from os import environ
from pathlib import Path
from unittest.mock import Mock

import pytest

from pyscaffold import api, cli
from pyscaffold import file_system as fs
from pyscaffold.extensions import venv

from ..helpers import ArgumentParser, disable_import, rmpath, uniqstr

# ---- "Isolated" tests ----


def parse(*args, set_defaults=None):
    parser = ArgumentParser()
    parser.set_defaults(**(set_defaults or {}))
    venv.Venv().augment_cli(parser)
    return vars(parser.parse_args(args))


def test_cli_opts():
    # no opts
    opts = parse()
    assert "venv" not in opts
    assert "venv_install" not in opts
    assert not opts.get("extensions")
    # opt but no value
    opts = parse("--venv")
    assert opts["venv"] == Path(".venv")
    assert [e.name for e in opts["extensions"]] == ["venv"]
    # opt and value
    opts = parse("--venv", ".here")
    assert opts["venv"] == Path(".here")
    # venv-install
    opts = parse("--venv-install", "appdirs>=1.1,<2", "six")
    opts = parse("--venv-install", "appdirs>=1.1,<2", "six")
    assert opts["venv_install"] == ["appdirs>=1.1,<2", "six"]
    assert [e.name for e in opts["extensions"]] == ["venv"]
    # venv-install but no value
    with pytest.raises((ArgumentError, TypeError, SystemExit)):
        # ^  TypeError happens because argparse tries to iterate over the --config opts
        #    since it is marked with nargs='+'
        #    ArgumentError and SystemExit might happen depending on the version
        #    of Python when there is a parse error.
        opts = parse("--venv-install")


def test_with_virtualenv_available(monkeypatch, tmpfolder):
    # When virtualenv is available
    virtualenv_mock = Mock()
    monkeypatch.setattr(venv, "create_with_virtualenv", virtualenv_mock)
    venv.run({}, {"project_path": Path(tmpfolder), "venv": ".venv"})
    # it will be called
    virtualenv_mock.assert_called_once()


@disable_import("virtualenv")
def test_without_virtualenv_available(monkeypatch, tmpfolder):
    # When virtualenv is not available
    venv_mock = Mock()
    monkeypatch.setattr(venv, "create_with_stdlib", venv_mock)
    venv.run({}, {"project_path": Path(tmpfolder), "venv": ".venv"})
    # venv will be called
    venv_mock.assert_called_once()


@disable_import("virtualenv")
@disable_import("venv")
def test_with_none_available(tmpfolder):
    # When virtualenv and venv are not available
    # then an exception will be raised
    with pytest.raises(venv.NotInstalled):
        venv.run({}, {"project_path": Path(tmpfolder), "venv": ".venv"})


def test_already_exists(monkeypatch, tmpfolder):
    virtualenv_mock = Mock()
    venv_mock = Mock()
    monkeypatch.setattr(venv, "create_with_virtualenv", virtualenv_mock)
    monkeypatch.setattr(venv, "create_with_stdlib", venv_mock)
    # When the venv directory already exist
    (Path(tmpfolder) / ".venv").mkdir()
    venv.run({}, {"project_path": Path(tmpfolder), "venv": ".venv"})
    # It should skip
    virtualenv_mock.assert_not_called()
    venv_mock.assert_not_called()


# ---- Integration tests ----


@pytest.mark.slow
@pytest.mark.parametrize(
    "creator, pretend",
    product((venv.create_with_virtualenv, venv.create_with_stdlib), (True, False)),
)
def test_creators(tmp_path_factory, creator, pretend):
    folder = tmp_path_factory.mktemp(f"test_creators_{uniqstr()}_")
    with fs.chdir(folder):  # ensure parametrized tests do not share folders
        path = Path(".venv")
        try:
            creator(path, pretend=pretend)
        except Exception:
            if environ.get("USING_CONDA") == "true":
                pytest.skip(
                    "Creating venvs more than one level deep inside conda is tricky"
                    "and error prone. Here we use at least 2 levels (tox > venv)."
                )
            else:
                raise

        if pretend:
            assert not path.exists()
        else:
            assert path.is_dir()
            assert list(path.glob("*/python*"))
            assert list(path.glob("*/pip*"))

    rmpath(folder)


@pytest.mark.slow
def test_install_packages(venv_path, tmpfolder):
    venv_path = Path(str(venv_path)).resolve()
    tmp = Path(str(tmpfolder)).resolve()

    # Given packages are not installed
    for pkg in "pytest pip-compile".split():
        assert venv.get_executable(pkg, venv_path, False) is None

    # when we run install_packages
    opts = {
        "project_path": tmp,
        "venv": venv_path,
        "venv_install": ["pytest>=6.0.0", "pip-tools"],
    }
    venv.install_packages({}, opts)

    # then they should be installed
    for pkg in "pytest pip-compile".split():
        bin_dir = str(Path(venv.get_executable(pkg, venv_path, False)).parent)
        assert bin_dir.lower().startswith(str(venv_path).lower())


def test_install_packages_no_pip(venv_path, tmpfolder, monkeypatch):
    venv_path = Path(str(venv_path)).resolve()
    tmp = Path(str(tmpfolder)).resolve()

    # Given pip is not installed
    monkeypatch.setattr(venv, "get_command", Mock(return_value=None))

    # when we run install_packages
    opts = {
        "project_path": tmp,
        "venv": venv_path,
        "venv_install": ["pytest>=6.0.0", "pip-tools"],
    }
    with pytest.raises(venv.NotInstalled) as ex:
        # Then it should throw an exception
        venv.install_packages({}, opts)

    assert "pip cannot be found" in str(ex)


@pytest.mark.slow
def test_api_with_venv(tmpfolder):
    venv_path = Path(tmpfolder) / "proj/.venv"
    # Given the venv does not exist yet
    assert not venv_path.exists()
    # when the CLI is invoked with --venv and --venv-install
    api.create_project(
        project_path="proj", extensions=[venv.Venv()], venv_install=["pytest>=6.0.0"]
    )
    # then the venv will be created accordingly
    assert venv_path.is_dir()
    # with python, pip and the installed executables
    assert list(venv_path.glob("*/python*"))
    assert list(venv_path.glob("*/pip*"))
    assert list(venv_path.glob("*/pytest*"))


@pytest.mark.slow
def test_cli_with_venv(tmpfolder):
    venv_path = Path(tmpfolder) / "proj/.venv"
    # Given the venv does not exist yet
    assert not venv_path.exists()
    # when the CLI is invoked with --venv and --venv-install
    cli.main(["proj", "--venv", "--venv-install", "pytest>=6.0.0"])
    # then the venv will be created accordingly
    assert venv_path.is_dir()
    # with python, pip and the installed executables
    assert list(venv_path.glob("*/python*"))
    assert list(venv_path.glob("*/pip*"))
    assert list(venv_path.glob("*/pytest*"))


@pytest.mark.slow
def test_cli_with_venv_and_pretend(tmpfolder):
    proj_path = Path(tmpfolder) / "proj"
    venv_path = proj_path / ".venv"
    # Given the venv does not exist yet
    assert not venv_path.exists()
    # when the CLI is invoked with --venv, --venv-install and --pretend
    cli.main(["proj", "--pretend", "--venv", "--venv-install", "pytest>=6.0.0"])
    # then the venv will not be created, or even the project itself
    assert not venv_path.exists()
    assert not proj_path.exists()
