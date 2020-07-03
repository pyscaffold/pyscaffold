#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import no_skeleton


def test_create_project_wit_no_skeleton(tmpfolder):
    # Given options with the tox extension,
    opts = dict(project="proj", extensions=[no_skeleton.NoSkeleton("no-skeleton")])

    # when the project is created,
    create_project(opts)

    # then skeleton file should not exist
    assert not path_exists("proj/src/proj/skeleton.py")
    assert not path_exists("proj/tests/test_skeleton.py")


def test_create_project_without_no_skeleton(tmpfolder):
    # Given options without the tox extension,
    opts = dict(project="proj")

    # when the project is created,
    create_project(opts)

    # then skeleton file should exist
    assert path_exists("proj/src/proj/skeleton.py")
    assert path_exists("proj/tests/test_skeleton.py")


def test_cli_with_no_skeleton(tmpfolder):
    # Given the command line with the tox option,
    sys.argv = ["pyscaffold", "--no-skeleton", "proj"]

    # when pyscaffold runs,
    run()

    # then skeleton file should not exist
    assert not path_exists("proj/src/proj/skeleton.py")
    assert not path_exists("proj/tests/test_skeleton.py")


def test_cli_without_no_skeleton(tmpfolder):
    # Given the command line without the tox option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then skeleton file should exist
    assert path_exists("proj/src/proj/skeleton.py")
    assert path_exists("proj/tests/test_skeleton.py")
