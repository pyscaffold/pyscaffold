#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions import travis

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


def test_create_project_with_travis(tmpfolder):
    # Given options with the travis extension,
    opts = dict(project="proj", extensions=[travis.extend_project])

    # when the project is created,
    create_project(opts)

    # then travis files should exist
    assert path_exists("proj/.travis.yml")
    assert path_exists("proj/tests/travis_install.sh")


def test_create_project_without_travis(tmpfolder):
    # Given options without the travis extension,
    opts = dict(project="proj")

    # when the project is created,
    create_project(opts)

    # then travis files should not exist
    assert not path_exists("proj/.travis.yml")
    assert not path_exists("proj/tests/travis_install.sh")


def test_cli_with_travis(tmpfolder):  # noqa
    # Given the command line with the travis option,
    sys.argv = ["pyscaffold", "--with-travis", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should exist
    assert path_exists("proj/.travis.yml")
    assert path_exists("proj/tests/travis_install.sh")


def test_cli_without_travis(tmpfolder):  # noqa
    # Given the command line without the travis option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should not exist
    assert not path_exists("proj/.travis.yml")
    assert not path_exists("proj/tests/travis_install.sh")
