#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
from os import environ
from os.path import exists as path_exists

import pytest

from pyscaffold.api import create_project
from pyscaffold.cli import run, parse_args
from pyscaffold.extensions import cookiecutter
from pyscaffold.templates import setup_py


PROJ_NAME = "proj"
COOKIECUTTER_URL = "https://github.com/audreyr/cookiecutter-pypackage.git"
COOKIECUTTER_FILES = ["proj/Makefile", "proj/.github/ISSUE_TEMPLATE.md"]


@pytest.fixture(autouse=True)
def cookiecutter_config(tmpfolder):
    # Define custom "cache" directories for cookiecutter inside a temporary
    # directory per test.
    # This way, if the tests are running in parallel, each test has its own
    # "cache" and stores/removes cookiecutter templates in an isolated way
    # avoiding inconsistencies/race conditions.
    config = (
        'cookiecutters_dir: "{dir}/custom-cookiecutters"\n'
        'replay_dir: "{dir}/cookiecutters-replay"'
    ).format(dir=str(tmpfolder))

    tmpfolder.mkdir('custom-cookiecutters')
    tmpfolder.mkdir('cookiecutters-replay')

    config_file = tmpfolder.join('cookiecutter.yaml')
    config_file.write(config)
    environ['COOKIECUTTER_CONFIG'] = str(config_file)

    yield

    del environ['COOKIECUTTER_CONFIG']


@pytest.mark.slow
def test_create_project_with_cookiecutter(tmpfolder):
    # Given options with the cookiecutter extension,
    opts = dict(project=PROJ_NAME,
                cookiecutter=COOKIECUTTER_URL,
                extensions=[cookiecutter.Cookiecutter('cookiecutter')])

    # when the project is created,
    create_project(opts)

    # then cookiecutter files should exist
    for path in COOKIECUTTER_FILES:
        assert path_exists(path)
    # and also overwritable pyscaffold files (with the exact contents)
    tmpfolder.join(PROJ_NAME).join("setup.py").read() == setup_py(opts)


def test_pretend_create_project_with_cookiecutter(tmpfolder, caplog):
    # Given options with the cookiecutter extension,
    opts = parse_args(
        [PROJ_NAME, '--pretend', '--cookiecutter', COOKIECUTTER_URL])

    # when the project is created,
    create_project(opts)

    # then files should exist
    assert not path_exists(PROJ_NAME)
    for path in COOKIECUTTER_FILES:
        assert not path_exists(path)

    # but activities should be logged
    assert re.search(r'run\s+cookiecutter', caplog.text)


def test_create_project_with_cookiecutter_but_no_template(tmpfolder):
    # Given options with the cookiecutter extension, but no template
    opts = dict(project=PROJ_NAME,
                extensions=[cookiecutter.Cookiecutter('cookiecutter')])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(cookiecutter.MissingTemplate):
        create_project(opts)


def test_create_project_without_cookiecutter(tmpfolder):
    # Given options without the cookiecutter extension,
    opts = dict(project=PROJ_NAME)

    # when the project is created,
    create_project(opts)

    # then cookiecutter files should not exist
    for path in COOKIECUTTER_FILES:
        assert not path_exists(path)


def test_create_project_no_cookiecutter(tmpfolder, nocookiecutter_mock):
    # Given options with the cookiecutter extension,
    # but without cookiecutter being installed,
    opts = dict(project=PROJ_NAME,
                cookiecutter=COOKIECUTTER_URL,
                extensions=[cookiecutter.Cookiecutter('cookiecutter')])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(cookiecutter.NotInstalled):
        create_project(opts)


@pytest.mark.slow
def test_cli_with_cookiecutter(tmpfolder):
    # Given the command line with the cookiecutter option,
    sys.argv = ["pyscaffold", PROJ_NAME,
                "--cookiecutter", COOKIECUTTER_URL]

    # when pyscaffold runs,
    run()

    # then cookiecutter files should exist
    for path in COOKIECUTTER_FILES:
        assert path_exists(path)


def test_cli_with_cookiecutter_but_no_template(tmpfolder, capsys):
    # Given the command line with the cookiecutter option, but no template
    sys.argv = ["pyscaffold", PROJ_NAME, "--cookiecutter"]

    # when pyscaffold runs,
    # then an exception should be raised.
    with pytest.raises(SystemExit):
        run()

    # make sure the exception is related to the missing argument
    out, err = capsys.readouterr()
    assert "--cookiecutter: expected one argument" in out + err


def test_cli_without_cookiecutter(tmpfolder):
    # Given the command line without the cookiecutter option,
    sys.argv = ["pyscaffold", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then cookiecutter files should not exist
    for path in COOKIECUTTER_FILES:
        assert not path_exists(path)
