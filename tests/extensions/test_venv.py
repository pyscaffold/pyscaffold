import sys
from itertools import product
from pathlib import Path
from unittest.mock import Mock

import pytest

from pyscaffold import cli
from pyscaffold.extensions import venv
from pyscaffold.shell import ShellCommandException

from ..helpers import ArgumentParser, disable_import, uniqstr

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
    with pytest.raises(TypeError):
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


def test_get_bin_path():
    # Quickest way of running that without installing anything / creating a venv
    # is to consider sys.prefix a venv
    python = Path(sys.executable).resolve()
    bin_path = venv.get_bin_path("python", venv_path=sys.prefix)
    assert bin_path.stem in python.stem
    assert bin_path.parent == python.parent
    with pytest.raises(venv.NotInstalled):
        venv.get_bin_path(uniqstr(), venv_path=sys.prefix)


def test_get_command():
    python = venv.get_command("python", venv_path=sys.prefix)
    assert next(python("--version")).strip().startswith("Python 3")
    with pytest.raises(ShellCommandException):
        python("--" + uniqstr())


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
def test_install_packages(venv_path, tmpfolder):
    venv_path = Path(str(venv_path)).resolve()
    tmp = Path(str(tmpfolder)).resolve()

    # Given packages are not installed
    for pkg in "pytest pip-compile".split():
        with pytest.raises(venv.NotInstalled):
            venv.get_bin_path(pkg, tmp, venv_path)

    # when we run install_packages
    opts = {
        "project_path": tmp,
        "venv": venv_path,
        "venv_install": ["pytest>=6.0.0", "pip-tools"],
    }
    venv.install_packages({}, opts)

    # then they should be installed
    for pkg in "pytest pip-compile".split():
        bin_path = venv.get_bin_path(pkg, tmp, venv_path)
        assert str(bin_path.parent).lower().startswith(str(venv_path).lower())


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
