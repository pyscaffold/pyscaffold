#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import tox


def test_create_project_with_tox(tmpfolder):
    # Given options with the tox extension,
    opts = dict(project="proj", extensions=[tox.Tox("tox")])

    # when the project is created,
    create_project(opts)

    # then tox files should exist
    assert path_exists("proj/tox.ini")


def test_create_project_without_tox(tmpfolder):
    # Given options without the tox extension,
    opts = dict(project="proj")

    # when the project is created,
    create_project(opts)

    # then tox files should not exist
    assert not path_exists("proj/tox.ini")


def test_cli_with_tox(tmpfolder):
    # Given the command line with the tox option,
    sys.argv = ["pyscaffold", "--tox", "proj"]

    # when pyscaffold runs,
    run()

    # then tox files should exist
    assert path_exists("proj/tox.ini")


def test_cli_without_tox(tmpfolder):
    # Given the command line without the tox option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then tox files should not exist
    assert not path_exists("proj/tox.ini")
