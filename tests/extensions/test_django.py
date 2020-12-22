#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
import sys
from os.path import exists as path_exists

import pytest

from pyscaffold import __version__ as pyscaffold_version
from pyscaffold.api import create_project
from pyscaffold.cli import parse_args, process_opts, run
from pyscaffold.extensions import django
from pyscaffold.templates import setup_py

skip_py33 = pytest.mark.skipif(
    sys.version_info[:2] == (3, 3), reason="django-admin.py fails with Python 3.3"
)

PROJ_NAME = "proj"
DJANGO_FILES = ["proj/manage.py", "proj/src/proj/wsgi.py"]


@skip_py33
@pytest.mark.slow
def test_create_project_with_django(tmpfolder):
    # Given options with the django extension,
    opts = dict(
        project=PROJ_NAME,
        extensions=[django.Django("django")],
        version=pyscaffold_version,
    )

    # when the project is created,
    create_project(opts)

    # then django files should exist
    for path in DJANGO_FILES:
        assert path_exists(path)
    # and also overwritable pyscaffold files (with the exact contents)
    assert tmpfolder.join(PROJ_NAME).join("setup.py").read() == setup_py(opts)


@skip_py33
def test_pretend_create_project_with_django(tmpfolder, caplog):
    # Given options with the django extension,
    caplog.set_level(logging.INFO)
    opts = parse_args([PROJ_NAME, "--pretend", "--django"])
    opts = process_opts(opts)

    # when the project is created,
    create_project(opts)

    # then files should exist
    assert not path_exists(PROJ_NAME)
    for path in DJANGO_FILES:
        assert not path_exists(path)

    # but activities should be logged
    logs = caplog.text
    assert re.search(r"run.+django", logs)


def test_create_project_without_django(tmpfolder):
    # Given options without the django extension,
    opts = dict(project=PROJ_NAME)

    # when the project is created,
    create_project(opts)

    # then django files should not exist
    for path in DJANGO_FILES:
        assert not path_exists(path)


def test_create_project_no_django(tmpfolder, nodjango_admin_mock):
    # Given options with the django extension,
    # but without django-admin being installed,
    opts = dict(project=PROJ_NAME, extensions=[django.Django("django")])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(django.DjangoAdminNotInstalled):
        create_project(opts)


@skip_py33
@pytest.mark.slow
def test_cli_with_django(tmpfolder):
    # Given the command line with the django option,
    sys.argv = ["pyscaffold", "--django", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then django files should exist
    for path in DJANGO_FILES:
        assert path_exists(path)


def test_cli_without_django(tmpfolder):
    # Given the command line without the django option,
    sys.argv = ["pyscaffold", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then django files should not exist
    for path in DJANGO_FILES:
        assert not path_exists(path)


def test_cli_with_django_and_update(tmpfolder, capsys):
    # Given a project exists
    create_project(project=PROJ_NAME)

    # when the project is updated
    # with the django extension,
    sys.argv = ["pyscaffold", PROJ_NAME, "--update", "--django"]
    run()

    # then a warning should be displayed
    out, err = capsys.readouterr()
    assert all(
        warn in out + err
        for warn in ("external tools", "not supported", "will be ignored")
    )
