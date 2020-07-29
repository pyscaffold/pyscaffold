from itertools import product
from pathlib import Path
from unittest.mock import Mock

import pytest

from pyscaffold import cli
from pyscaffold.extensions import venv

from ..helpers import ArgumentParser, disable_import

# ---- "Isolated" tests ----


def parse(*args, set_defaults={}):
    parser = ArgumentParser()
    parser.set_defaults(**set_defaults)
    venv.Venv().augment_cli(parser)
    return vars(parser.parse_args(args))


def test_cli_opts():
    # no opts
    opts = parse()
    assert "venv" not in opts
    # opt but no value
    opts = parse("--venv")
    assert opts["venv"] == Path(".venv")
    # opt and value
    opts = parse("--venv", ".here")
    assert opts["venv"] == Path(".here")


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
def test_creators(tmpfolder, creator, pretend):
    path = Path(".venv")
    creator(path, pretend=pretend)
    if pretend:
        assert not path.exists()
    else:
        assert path.is_dir()
        assert list(path.glob("*/python*"))
        assert list(path.glob("*/pip*"))


@pytest.mark.slow
def test_cli_with_venv(tmpfolder):
    venv_path = Path(tmpfolder) / "proj/.venv"
    # Given the venv does not exist yet
    assert not venv_path.exists()
    # when the CLI is invoked with --save-config
    cli.main(["proj", "--venv"])
    # then the venv will be created accordingly
    assert venv_path.is_dir()
    # with a python and pip executables
    assert list(venv_path.glob("*/python*"))
    assert list(venv_path.glob("*/pip*"))
