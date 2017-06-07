#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
from contextlib import contextmanager
from imp import reload
from shutil import rmtree
from subprocess import CalledProcessError

import pkg_resources

import pyscaffold
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
def tmpfolder(tmpdir):
    old_path = os.getcwd()
    newpath = str(tmpdir)
    os.chdir(newpath)
    try:
        yield tmpdir
    finally:
        os.chdir(old_path)
        rmtree(newpath, onerror=set_writable)


@pytest.yield_fixture()
def git_mock():
    def mock(*_):
        yield "git@mock"

    old_git = shell.git
    shell.git = mock
    try:
        yield
    finally:
        shell.git = old_git


@pytest.yield_fixture()
def nogit_mock():
    def raise_error(*_):
        raise CalledProcessError(1, "git", "No git mock!")

    old_git = shell.git
    shell.git = raise_error
    try:
        yield
    finally:
        shell.git = old_git


@pytest.yield_fixture()
def nonegit_mock():
    old_git = shell.git
    shell.git = None
    try:
        yield
    finally:
        shell.git = old_git


@pytest.yield_fixture()
def noconfgit_mock():
    def raise_error(*argv):
        if 'config' in argv:
            raise CalledProcessError(1, "git", "No git mock!")

    old_git = shell.git
    shell.git = raise_error
    try:
        yield
    finally:
        shell.git = old_git


@pytest.yield_fixture()
def nodjango_admin_mock():
    def raise_error(*_):
        raise CalledProcessError(1, "django_admin.py", "No django_admin mock!")

    old_django_admin = shell.django_admin
    shell.django_admin = raise_error
    try:
        yield
    finally:
        shell.django_admin = old_django_admin


@contextmanager
def disable_import(prefix):
    """Avoid packages being imported

    Args:
        prefix: string at the beginning of the package name
    """
    try:
        # First try python 2.7.x
        # (for some recent versions the `builtins` module is available,
        # but it behaves differently from the one in 3.x)
        import __builtin__ as builtins
    except ImportError:
        import builtins
    realimport = builtins.__import__

    def my_import(name, *args):
        if name.startswith(prefix):
            raise ImportError
        return realimport(name, *args)

    try:
        builtins.__import__ = my_import
        yield
    finally:
        builtins.__import__ = realimport


@pytest.yield_fixture()
def nocookiecutter_mock():
    with disable_import('cookiecutter'):
        yield


@pytest.yield_fixture()
def old_setuptools_mock():
    with disable_import('pkg_resources'):
        yield


@pytest.yield_fixture()
def nosphinx_mock():
    with disable_import('sphinx'):
        yield


@pytest.yield_fixture()
def get_distribution_raises_exception():
    def raise_exeception():
        raise RuntimeError("No get_distribution mock")
    orig_get_distribution = pkg_resources.get_distribution
    pkg_resources.get_distribution = raise_exeception
    reload(pyscaffold)
    try:
        yield
    finally:
        pkg_resources.get_distribution = orig_get_distribution
        reload(pyscaffold)
