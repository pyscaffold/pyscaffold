#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys

import pytest
from pyscaffold import cli
from pyscaffold.exceptions import OldSetuptools

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


def test_main(tmpfolder, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    assert os.path.exists(args[0])


def test_main_when_updating(tmpfolder, capsys, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    args = ["--update", "my-project"]
    cli.main(args)
    assert os.path.exists(args[1])
    out, _ = capsys.readouterr()
    assert "Update accomplished!" in out


def test_run(tmpfolder, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    cli.run()
    assert os.path.exists(sys.argv[1])
