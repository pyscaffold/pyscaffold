#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.cli import create_project, get_default_opts, run
from pyscaffold.extensions import travis

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


def test_create_project_with_travis(tmpdir):
    # Given options with the travis extension,
    opts = get_default_opts("proj", extensions=[travis.extend_project])

    # when the project is created,
    create_project(opts)

    # then travis files should exist
    assert path_exists("proj/.travis.yml")
    assert path_exists("proj/tests/travis_install.sh")


def test_create_project_without_travis(tmpdir):
    # Given options without the travis extension,
    opts = get_default_opts("proj")

    # when the project is created,
    create_project(opts)

    # then travis files should not exist
    assert not path_exists("proj/.travis.yml")
    assert not path_exists("proj/tests/travis_install.sh")


def test_cli_with_travis(tmpdir):  # noqa
    # Given the command line with the travis option,
    sys.argv = ["pyscaffold", "--with-travis", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should exist
    assert path_exists("proj/.travis.yml")
    assert path_exists("proj/tests/travis_install.sh")


def test_cli_without_travis(tmpdir):  # noqa
    # Given the command line without the travis option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then travis files should not exist
    assert not path_exists("proj/.travis.yml")
    assert not path_exists("proj/tests/travis_install.sh")
