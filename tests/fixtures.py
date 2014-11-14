#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
import tempfile
from shutil import rmtree
from subprocess import CalledProcessError

import pytest
from pyscaffold import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def set_writable(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


@pytest.yield_fixture()
def tmpdir():
    old_path = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    os.chdir(old_path)
    rmtree(newpath, onerror=set_writable)


@pytest.yield_fixture()
def git_mock():
    def mock(*_):
        yield "git@mock"

    old_git = shell.git
    shell.git = mock
    yield
    shell.git = old_git


@pytest.yield_fixture()
def nogit_mock():
    def raise_error(*_):
        raise CalledProcessError(1, "git", "No git mock!")

    old_git = shell.git
    shell.git = raise_error
    yield
    shell.git = old_git


@pytest.yield_fixture()
def noconfgit_mock():
    def raise_error(*argv):
        if 'config' in argv:
            raise CalledProcessError(1, "git", "No git mock!")

    old_git = shell.git
    shell.git = raise_error
    yield
    shell.git = old_git


@pytest.yield_fixture()
def nodjango_admin_mock():
    def raise_error(*_):
        raise CalledProcessError(1, "django_admin.py", "No django_admin mock!")

    old_django_admin = shell.django_admin
    shell.django_admin = raise_error
    yield
    shell.django_admin = old_django_admin
