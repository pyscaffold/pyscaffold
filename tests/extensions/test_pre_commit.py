#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from unittest.mock import Mock

from pyscaffold import shell
from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import pre_commit
from pyscaffold.templates import get_template


def assert_in_logs(caplog, *expected):
    log = caplog.text
    for text in expected:
        assert text in log


# ---- "Isolated" tests ----


def test_find_executable(monkeypatch):
    # When an executable can be found
    exec = Mock()
    monkeypatch.setattr(shell, "get_command", Mock(return_value=exec))
    _, opts = pre_commit.find_executable({}, {})
    # then pre-commit should no be added to venv_install
    assert "pre-commit" not in opts.get("venv_install", [])
    # and the command should be stored in opts
    assert opts[pre_commit.CMD_OPT] == exec

    # When an executable can not be found
    monkeypatch.setattr(shell, "get_command", Mock(return_value=None))
    _, opts = pre_commit.find_executable({}, {})
    # then pre-commit should be added to venv_install
    assert "pre-commit" in opts.get("venv_install", [])
    # and the command should not be stored in opts
    assert pre_commit.CMD_OPT not in opts


def test_install(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    # When an executable can be found
    exec = Mock()
    monkeypatch.setattr(shell, "get_command", Mock(return_value=exec))
    pre_commit.install({}, {})
    # then `pre-commit` install should run
    assert exec.called
    args, _ = exec.call_args
    assert "install" in args

    # When no executable can be found
    monkeypatch.setattr(shell, "get_command", Mock(return_value=None))
    pre_commit.install({}, {})
    # then the proper log message should be displayed
    msg = pre_commit.INSTALL_MSG.format(project_path="PROJECT_DIR")
    assert_in_logs(caplog, msg)

    # When an error occurs during installation
    caplog.set_level(logging.ERROR)
    exec = Mock(side_effect=shell.ShellCommandException)
    monkeypatch.setattr(shell, "get_command", Mock(return_value=exec))
    # then PyScaffold should not stop, only log the error.
    pre_commit.install({}, {})
    assert_in_logs(caplog, pre_commit.ERROR_MSG)

    # When a command is available in opts
    cmd = Mock()
    exec = Mock()
    monkeypatch.setattr(shell, "get_command", Mock(return_value=exec))
    # then it should be ussed, and get_command not called
    pre_commit.install({}, {pre_commit.CMD_OPT: cmd})
    assert cmd.called
    args, _ = cmd.call_args
    assert "install" in args
    assert not exec.called


def test_add_instructions():
    old_text = get_template("readme")
    opts = {"title": "proj", "name": "proj", "description": "desc", "version": "99.9"}
    new_text, _ = pre_commit.add_instructions(opts, old_text, Mock())
    note = pre_commit.README_NOTE.format(**opts)
    assert note in new_text


# ---- Integration tests ----


def test_create_project_with_pre_commit(tmpfolder, caplog):
    caplog.set_level(logging.WARNING)
    # Given options with the pre-commit extension,
    opts = dict(project_path="proj", extensions=[pre_commit.PreCommit("pre-commit")])

    # when the project is created,
    create_project(opts)

    # then pre-commit files should exist
    assert Path("proj/.pre-commit-config.yaml").exists()
    assert Path("proj/.isort.cfg").exists()
    note = pre_commit.README_NOTE.format(name="proj")
    assert note in Path("proj/README.rst").read_text()

    # and the user should be instructed to update pre-commit
    assert_in_logs(caplog, pre_commit.UPDATE_MSG)


def test_create_project_without_pre_commit(tmpfolder):
    # Given options without the pre-commit extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then pre-commit files should not exist
    assert not Path("proj/.pre-commit-config.yaml").exists()
    assert not Path("proj/.isort.cfg").exists()


def test_cli_with_pre_commit(tmpfolder):
    # Given the command line with the pre-commit option,
    sys.argv = ["pyscaffold", "--pre-commit", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should exist
    assert Path("proj/.pre-commit-config.yaml").exists()
    assert Path("proj/.isort.cfg").exists()


def test_cli_with_pre_commit_or_pretend(tmpfolder):
    # Given the command line with the pre-commit option and pretend
    sys.argv = ["pyscaffold", "--pretend", "--pre-commit", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should not exist (or the project itself)
    assert not Path("proj/.pre-commit-config.yaml").exists()
    assert not Path("proj").exists()


def test_cli_without_pre_commit(tmpfolder):
    # Given the command line without the pre-commit option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should not exist
    assert not Path("proj/.pre-commit-config.yaml").exists()
    assert not Path("proj/.isort.cfg").exists()
