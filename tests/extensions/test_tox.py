#!/usr/bin/env python
import sys
from pathlib import Path

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import tox


def test_create_project_with_tox(tmpfolder):
    # Given options with the tox extension,
    opts = dict(project_path="proj", extensions=[tox.Tox("tox")])

    # when the project is created,
    create_project(opts)

    # then tox files should exist
    assert Path("proj/tox.ini").exists()


def test_create_project_without_tox(tmpfolder):
    # Given options without the tox extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then tox files should not exist
    assert not Path("proj/tox.ini").exists()


def test_cli_with_tox(tmpfolder):
    # Given the command line with the tox option,
    sys.argv = ["pyscaffold", "--tox", "proj"]

    # when pyscaffold runs,
    run()

    # then tox files should exist
    assert Path("proj/tox.ini").exists()


def test_cli_without_tox(tmpfolder):
    # Given the command line without the tox option,
    sys.argv = ["pyscaffold", "proj", "-vv"]

    # when pyscaffold runs,
    run()

    # then tox files should not exist
    assert not Path("proj/tox.ini").exists()
