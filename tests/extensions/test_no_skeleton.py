#!/usr/bin/env python
import sys
from pathlib import Path

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import no_skeleton


def test_create_project_wit_no_skeleton(tmpfolder):
    # Given options with the no-skeleton extension,
    opts = dict(project_path="proj", extensions=[no_skeleton.NoSkeleton("no-skeleton")])

    # when the project is created,
    create_project(opts)

    # then skeleton file should not exist
    assert not Path("proj/src/proj/skeleton.py").exists()
    assert not Path("proj/tests/test_skeleton.py").exists()


def test_create_project_without_no_skeleton(tmpfolder):
    # Given options without the no-skeleton extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then skeleton file should exist
    assert Path("proj/src/proj/skeleton.py").exists()
    assert Path("proj/tests/test_skeleton.py").exists()


def test_cli_with_no_skeleton(tmpfolder):
    # Given the command line with the no-skeleton option,
    sys.argv = ["pyscaffold", "--no-skeleton", "proj"]

    # when pyscaffold runs,
    run()

    # then skeleton file should not exist
    assert not Path("proj/src/proj/skeleton.py").exists()
    assert not Path("proj/tests/test_skeleton.py").exists()


def test_cli_with_no_skeleton_and_pretend(tmpfolder):
    # Given the command line with the no-skeleton and pretend options,
    sys.argv = ["pyscaffold", "--pretend", "--no-skeleton", "proj"]

    # when pyscaffold runs,
    run()

    # then skeleton file should not exist (or the project itself)
    assert not Path("proj/src/proj/skeleton.py").exists()
    assert not Path("proj").exists()


def test_cli_without_no_skeleton(tmpfolder):
    # Given the command line without the no-skeleton option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then skeleton file should exist
    assert Path("proj/src/proj/skeleton.py").exists()
    assert Path("proj/tests/test_skeleton.py").exists()
