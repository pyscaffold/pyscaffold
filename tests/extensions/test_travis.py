#!/usr/bin/env python
import sys
from pathlib import Path

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import travis


def test_create_project_with_travis(tmpfolder):
    # Given options with the travis extension,
    opts = dict(project_path="proj", extensions=[travis.Travis("travis")])

    # when the project is created,
    create_project(opts)

    # then travis files should exist
    assert Path("proj/.travis.yml").exists()
    assert Path("proj/tests/travis_install.sh").exists()


def test_create_project_without_travis(tmpfolder):
    # Given options without the travis extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then travis files should not exist
    assert not Path("proj/.travis.yml").exists()
    assert not Path("proj/tests/travis_install.sh").exists()


def test_cli_with_travis(tmpfolder):
    # Given the command line with the travis option,
    sys.argv = ["pyscaffold", "--travis", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should exist
    assert Path("proj/.travis.yml").exists()
    assert Path("proj/tests/travis_install.sh").exists()


def test_cli_with_travis_and_pretend(tmpfolder):
    # Given the command line with the travis option and pretend
    sys.argv = ["pyscaffold", "--pretend", "--travis", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files (or the project itself) should not exist
    assert not Path("proj/.travis.yml").exists()
    assert not Path("proj/tests/travis_install.sh").exists()
    assert not Path("proj").exists()


def test_cli_without_travis(tmpfolder):
    # Given the command line without the travis option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should not exist
    assert not Path("proj/.travis.yml").exists()
    assert not Path("proj/tests/travis_install.sh").exists()
