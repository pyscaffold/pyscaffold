#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project, get_default_opts
from pyscaffold.cli import run
from pyscaffold.extensions import tox

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


def test_create_project_with_tox(tmpdir):
    # Given options with the tox extension,
    opts = get_default_opts("proj", extensions=[tox.extend_project])

    # when the project is created,
    create_project(opts)

    # then tox files should exist
    assert path_exists("proj/tox.ini")


def test_create_project_without_tox(tmpdir):
    # Given options without the tox extension,
    opts = get_default_opts("proj")

    # when the project is created,
    create_project(opts)

    # then tox files should not exist
    assert not path_exists("proj/tox.ini")


def test_cli_with_tox(tmpdir):  # noqa
    # Given the command line with the tox option,
    sys.argv = ["pyscaffold", "--with-tox", "proj"]

    # when pyscaffold runs,
    run()

    # then tox files should exist
    assert path_exists("proj/tox.ini")


def test_cli_without_tox(tmpdir):  # noqa
    # Given the command line without the tox option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then tox files should not exist
    assert not path_exists("proj/tox.ini")
