#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

from pyscaffold.cli import create_project, get_default_opts, run
from pyscaffold.extensions import pre_commit

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


def test_create_project_with_pre_commit(tmpdir):
    # Given options with the pre-commit extension,
    opts = get_default_opts("proj", extensions=[pre_commit.extend_project])

    # when the project is created,
    create_project(opts)

    # then pre-commit files should exist
    assert path_exists("proj/.pre-commit-config.yaml")


def test_create_project_without_pre_commit(tmpdir):
    # Given options without the pre-commit extension,
    opts = get_default_opts("proj")

    # when the project is created,
    create_project(opts)

    # then pre-commit files should not exist
    assert not path_exists("proj/.pre-commit-config.yaml")


def test_cli_with_pre_commit(tmpdir):  # noqa
    # Given the command line with the pre-commit option,
    sys.argv = ["pyscaffold", "--with-pre-commit", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should exist
    assert path_exists("proj/.pre-commit-config.yaml")


def test_cli_without_pre_commit(tmpdir):  # noqa
    # Given the command line without the pre-commit option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then pre-commit files should not exist
    assert not path_exists("proj/.pre-commit-config.yaml")
