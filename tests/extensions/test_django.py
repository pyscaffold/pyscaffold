#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

import pytest

from pyscaffold.cli import create_project, get_default_opts, run
from pyscaffold.extensions import django
from pyscaffold.templates import setup_py

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"

skip_py33 = pytest.mark.skipif(sys.version_info[:2] == (3, 3),
                               reason="django-admin.py fails with Python 3.3")

PROJ_NAME = "proj"
DJANGO_FILES = ["proj/manage.py", "proj/proj/wsgi.py"]


@skip_py33
def test_create_project_with_django(tmpdir):
    # Given options with the django extension,
    opts = get_default_opts(PROJ_NAME, extensions=[django.extend_project])

    # when the project is created,
    create_project(opts)

    # then django files should exist
    for path in DJANGO_FILES:
        assert path_exists(path)
    # and also overwritable pyscaffold files (with the exact contents)
    tmpdir.join(PROJ_NAME).join("setup.py").read() == setup_py(opts)


def test_create_project_without_django(tmpdir):
    # Given options without the django extension,
    opts = get_default_opts(PROJ_NAME)

    # when the project is created,
    create_project(opts)

    # then django files should not exist
    for path in DJANGO_FILES:
        assert not path_exists(path)


def test_create_project_no_django(tmpdir, nodjango_admin_mock):  # noqa
    # Given options with the django extension,
    # but without django-admin being installed,
    opts = get_default_opts(PROJ_NAME, extensions=[django.extend_project])

    # when the project is created,
    # then an exception should be raised.
    with pytest.raises(django.DjangoAdminNotInstalled):
        create_project(opts)


@skip_py33
def test_cli_with_django(tmpdir):  # noqa
    # Given the command line with the django option,
    sys.argv = ["pyscaffold", "--with-django", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then django files should exist
    for path in DJANGO_FILES:
        assert path_exists(path)


def test_cli_without_django(tmpdir):  # noqa
    # Given the command line without the django option,
    sys.argv = ["pyscaffold", PROJ_NAME]

    # when pyscaffold runs,
    run()

    # then django files should not exist
    for path in DJANGO_FILES:
        assert not path_exists(path)
