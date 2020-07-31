#!/usr/bin/env python
import logging
import sys
from pathlib import Path

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import pre_commit


def test_create_project_with_pre_commit(tmpfolder, caplog):
    caplog.set_level(logging.WARNING)
    # Given options with the pre-commit extension,
    opts = dict(project_path="proj", extensions=[pre_commit.PreCommit("pre-commit")])

    # when the project is created,
    create_project(opts)

    # then pre-commit files should exist
    assert Path("proj/.pre-commit-config.yaml").exists()
    assert Path("proj/.isort.cfg").exists()

    # and the user should be instructed to install pre-commit
    expected_warnings = ("pre-commit autoupdate",)
    log = caplog.text
    for text in expected_warnings:
        assert text in log


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


def test_cli_without_pre_commit(tmpfolder):
    # Given the command line without the pre-commit option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should not exist
    assert not Path("proj/.pre-commit-config.yaml").exists()
    assert not Path("proj/.isort.cfg").exists()
