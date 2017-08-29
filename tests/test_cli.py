#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys

import pytest

from pyscaffold import cli
from pyscaffold.exceptions import OldSetuptools
from pyscaffold.log import logger

from .log_helpers import ansi_regex, find_report

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_parse_args():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts['project'] == "my-project"


def test_parse_args_with_old_setuptools(old_setuptools_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(OldSetuptools):
        cli.parse_args(args)


def test_parse_quiet_option():
    for quiet in ("--quiet", "-q"):
        args = ["my-project", quiet]
        opts = cli.parse_args(args)
        assert opts["log_level"] == logging.CRITICAL


def test_parse_default_log_level():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts["log_level"] == logging.INFO


def test_parse_pretend():
    for flag in ["--pretend", "--dry-run"]:
        opts = cli.parse_args(["my-project", flag])
        assert opts["pretend"]
    opts = cli.parse_args(["my-project"])
    assert not opts["pretend"]


def test_parse_list_actions():
    opts = cli.parse_args(["my-project", "--list-actions"])
    assert opts["command"] == cli.list_actions
    opts = cli.parse_args(["my-project"])
    assert opts["command"] == cli.run_scaffold


def test_main(tmpfolder, git_mock, caplog):  # noqa
    args = ["my-project"]
    cli.main(args)
    assert os.path.exists(args[0])

    # Check for some log messages
    assert find_report(caplog, 'invoke', 'get_default_options')
    assert find_report(caplog, 'invoke', 'verify_options_consistency')
    assert find_report(caplog, 'invoke', 'define_structure')
    assert find_report(caplog, 'invoke', 'create_structure')
    assert find_report(caplog, 'create', 'setup.py')
    assert find_report(caplog, 'create', 'requirements.txt')
    assert find_report(caplog, 'create', 'my_project/__init__.py')
    assert find_report(caplog, 'run', 'git init')
    assert find_report(caplog, 'run', 'git add')


def test_pretend_main(tmpfolder, git_mock, caplog):  # noqa
    for flag in ["--pretend", "--dry-run"]:
        args = ["my-project", flag]
        cli.main(args)
        assert not os.path.exists(args[0])

        # Check for some log messages
        assert find_report(caplog, 'invoke', 'get_default_options')
        assert find_report(caplog, 'invoke', 'verify_options_consistency')
        assert find_report(caplog, 'invoke', 'define_structure')
        assert find_report(caplog, 'invoke', 'create_structure')
        assert find_report(caplog, 'create', 'setup.py')
        assert find_report(caplog, 'create', 'requirements.txt')
        assert find_report(caplog, 'create', 'my_project/__init__.py')
        assert find_report(caplog, 'run', 'git init')
        assert find_report(caplog, 'run', 'git add')


def test_main_when_updating(tmpfolder, capsys, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    args = ["--update", "my-project"]
    cli.main(args)
    assert os.path.exists(args[1])
    out, _ = capsys.readouterr()
    assert "Update accomplished!" in out


def test_main_with_list_actions(capsys, reset_logger):
    # When putup is called with --list-actions,
    args = ["my-project", "--with-tox", "--list-actions"]
    cli.main(args)
    # then the action list should be printed,
    out, _ = capsys.readouterr()
    assert "Planned Actions" in out
    assert "pyscaffold.api:get_default_options" in out
    assert "pyscaffold.structure:define_structure" in out
    assert "pyscaffold.extensions.tox:add_files" in out
    assert "pyscaffold.structure:create_structure" in out
    assert "pyscaffold.api:init_git" in out
    # but no project should be created
    assert not os.path.exists(args[0])


def test_run(tmpfolder, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    cli.run()
    assert os.path.exists(sys.argv[1])


def test_configure_logger(monkeypatch, caplog, reset_logger):
    # Given an environment that supports color,
    monkeypatch.setattr('pyscaffold.termui.supports_color', lambda *_: True)
    # when configure_logger in called,
    opts = dict(log_level=logging.INFO)
    cli.configure_logger(opts)
    # then the formatter should be changed to use colors,
    logger.report('some', 'activity')
    out = caplog.text
    assert ansi_regex('some').search(out)
