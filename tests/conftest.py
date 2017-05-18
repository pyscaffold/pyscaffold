#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
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


# tmpdir is already a built-in fixture from pytest,
# so in order to override it without loosing its API,
# let's try this curious workaround:
@pytest.yield_fixture()
def tmpdir(tmpdir):
    _tmpdir = tmpdir  # original fixture from pytest
    old_path = os.getcwd()
    newpath = str(_tmpdir)
    os.chdir(newpath)
    try:
        yield _tmpdir
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


@pytest.yield_fixture()
def nosphinx_mock():
    try:
        import builtins
    except ImportError:
        import __builtin__ as builtins
    realimport = builtins.__import__

    def my_import(name, *args):
        if name.startswith('sphinx'):
            raise ImportError
        return realimport(name, *args)

    try:
        builtins.__import__ = my_import
        yield
    finally:
        builtins.__import__ = realimport


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
