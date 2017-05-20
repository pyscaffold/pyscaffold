#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

import pytest

from pyscaffold.cli import create_project, get_default_opts, run
from pyscaffold.extensions import cookiecutter
from pyscaffold.templates import setup_py

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"

PROJ_NAME = "proj"
COOKIECUTTER_URL = "https://github.com/audreyr/cookiecutter-pypackage.git"
COOKIECUTTER_FILES = ["proj/Makefile", "proj/.github/ISSUE_TEMPLATE.md"]


def test_create_project_with_cookiecutter(tmpdir):
    # Given options with the cookiecutter extension,
    opts = get_default_opts(PROJ_NAME,
                            cookiecutter_template=COOKIECUTTER_URL,
                            extensions=[cookiecutter.extend_project])

    # when the project is created,
    create_project(opts)

    # then cookiecutter files should exist
    for path in COOKIECUTTER_FILES:
        assert path_exists(path)
    # and also overwritable pyscaffold files (with the exact contents)
    tmpdir.join(PROJ_NAME).join("setup.py").read() == setup_py(opts)


def test_create_project_with_cookiecutter_but_no_template(tmpdir):
    # Given options with the cookiecutter extension, but no template
    opts = get_default_opts(PROJ_NAME,
                            extensions=[cookiecutter.extend_project])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(cookiecutter.MissingTemplate):
        create_project(opts)


def test_create_project_without_cookiecutter(tmpdir):
    # Given options without the cookiecutter extension,
    opts = get_default_opts(PROJ_NAME)

    # when the project is created,
    create_project(opts)

    # then cookiecutter files should not exist
    for path in COOKIECUTTER_FILES:
        assert not path_exists(path)

def test_create_project_no_cookiecutter(tmpdir, nocookiecutter_mock):  # noqa
    # Given options with the cookiecutter extension,
    # but without cookiecutter being installed,
    opts = get_default_opts(PROJ_NAME,
                            cookiecutter_template=COOKIECUTTER_URL,
                            extensions=[cookiecutter.extend_project])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(cookiecutter.NotInstalled):
        create_project(opts)


def test_cli_with_cookiecutter(tmpdir):  # noqa
    # Given the command line with the cookiecutter option,
    sys.argv = ["pyscaffold", PROJ_NAME,
                "--with-cookiecutter", COOKIECUTTER_URL]

    # when pyscaffold runs,
    run()

    # then cookiecutter files should exist
    for path in COOKIECUTTER_FILES:
        assert path_exists(path)


def test_cli_with_cookiecutter_but_no_template(tmpdir, capsys):  # noqa
    # Given the command line with the cookiecutter option, but no template
    sys.argv = ["pyscaffold", PROJ_NAME, "--with-cookiecutter"]

    # when pyscaffold runs,
    # then an exception should be raised.
    with pytest.raises(SystemExit):
        run()

    # make sure the exception is related to the missing argument
    out, err = capsys.readouterr()
    assert "--with-cookiecutter: expected one argument" in out + err


def test_cli_without_cookiecutter(tmpdir):  # noqa
    # Given the command line without the cookiecutter option,
    sys.argv = ["pyscaffold", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then cookiecutter files should not exist
    for path in COOKIECUTTER_FILES:
        assert not path_exists(path)
