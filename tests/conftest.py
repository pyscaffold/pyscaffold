#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import stat
from collections import namedtuple
from contextlib import contextmanager
from importlib import reload
from os.path import join as path_join
from os.path import isdir
from shutil import rmtree
from pkg_resources import DistributionNotFound

import pytest

from pyscaffold.exceptions import ShellCommandException

try:
    # First try python 2.7.x
    # (for some recent versions the `builtins` module is available,
    # but it behaves differently from the one in 3.x)
    import __builtin__ as builtins
except ImportError:
    import builtins


def nop(*args, **kwargs):
    """Function that does nothing"""


def obj(**kwargs):
    """Create a generic object with the given fields"""
    constructor = namedtuple('GenericObject', kwargs.keys())
    return constructor(**kwargs)


def set_writable(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


@pytest.fixture
def pyscaffold():
    return __import__('pyscaffold')


@pytest.fixture
def real_isatty():
    pyscaffold = __import__('pyscaffold', globals(), locals(), ['termui'])
    return pyscaffold.termui.isatty


@pytest.fixture
def logger():
    pyscaffold = __import__('pyscaffold', globals(), locals(), ['log'])
    return pyscaffold.log.logger


@pytest.fixture
def tmpfolder(tmpdir):
    old_path = os.getcwd()
    newpath = str(tmpdir)
    os.chdir(newpath)
    try:
        yield tmpdir
    finally:
        os.chdir(old_path)
        rmtree(newpath, onerror=set_writable)


@pytest.fixture
def git_mock(monkeypatch, logger):
    def _git(*args, **kwargs):
        cmd = ' '.join(['git'] + list(args))

        if kwargs.get('log', False):
            logger.report('run', cmd, context=os.getcwd())

        def _response():
            yield "git@mock"

        return _response()

    def _is_git_repo(folder):
        return isdir(path_join(folder, '.git'))

    monkeypatch.setattr('pyscaffold.shell.git', _git)
    monkeypatch.setattr('pyscaffold.repo.is_git_repo', _is_git_repo)

    yield _git


@pytest.fixture
def nogit_mock(monkeypatch):
    def raise_error(*_):
        raise ShellCommandException("No git mock!")

    monkeypatch.setattr('pyscaffold.shell.git', raise_error)
    yield


@pytest.fixture
def nonegit_mock(monkeypatch):
    monkeypatch.setattr('pyscaffold.shell.git', None)
    yield


@pytest.fixture
def noconfgit_mock(monkeypatch):
    def raise_error(*argv):
        if 'config' in argv:
            raise ShellCommandException("No git mock!")

    monkeypatch.setattr('pyscaffold.shell.git', raise_error)
    yield


@pytest.fixture
def nodjango_admin_mock(monkeypatch):
    def raise_error(*_):
        raise ShellCommandException("No django_admin mock!")

    monkeypatch.setattr('pyscaffold.shell.django_admin', raise_error)
    yield


@contextmanager
def disable_import(prefix):
    """Avoid packages being imported

    Args:
        prefix: string at the beginning of the package name
    """
    realimport = builtins.__import__

    def my_import(name, *args, **kwargs):
        if name.startswith(prefix):
            raise ImportError
        return realimport(name, *args, **kwargs)

    try:
        builtins.__import__ = my_import
        yield
    finally:
        builtins.__import__ = realimport


@contextmanager
def replace_import(prefix, new_module):
    """Make import return a fake module

    Args:
        prefix: string at the beginning of the package name
    """
    realimport = builtins.__import__

    def my_import(name, *args, **kwargs):
        if name.startswith(prefix):
            return new_module
        return realimport(name, *args, **kwargs)

    try:
        builtins.__import__ = my_import
        yield
    finally:
        builtins.__import__ = realimport


@pytest.fixture
def nocookiecutter_mock():
    with disable_import('cookiecutter'):
        yield


@pytest.fixture
def old_setuptools_mock():
    class OldSetuptools(object):
        __version__ = '10.0.0'

    with replace_import('setuptools', OldSetuptools):
        yield


@pytest.fixture
def nosphinx_mock():
    with disable_import('sphinx'):
        yield


@pytest.fixture
def get_distribution_raises_exception(monkeypatch, pyscaffold):
    def raise_exeception(name):
        raise DistributionNotFound("No get_distribution mock")

    monkeypatch.setattr('pkg_resources.get_distribution', raise_exeception)
    reload(pyscaffold)
    try:
        yield
    finally:
        monkeypatch.undo()
        reload(pyscaffold)


@pytest.fixture
def reset_logger():
    yield
    raw_logger = logging.getLogger('pyscaffold.log')
    raw_logger.setLevel(logging.NOTSET)

    for h in raw_logger.handlers:
        raw_logger.removeHandler(h)
    raw_logger.handlers = []

    from pyscaffold.log import ReportLogger, logger
    new_logger = ReportLogger()

    logger.handler = new_logger.handler
    logger.formatter = new_logger.formatter

    assert len(raw_logger.handlers) == 1
    assert raw_logger.handlers[0] == logger.handler


@pytest.fixture(autouse=True)
def no_isatty(monkeypatch, real_isatty):
    # Requiring real_isatty ensures processing that fixture
    # before this one. Therefore real_isatty is cached before the mock
    # replaces the real function.

    # Avoid ansi codes in tests, since capture fixtures seems to
    # emulate stdout and stdin behavior (including isatty method)
    monkeypatch.setattr('pyscaffold.termui.isatty', lambda *_: False)
    yield


@pytest.fixture
def orig_isatty(monkeypatch, real_isatty):
    monkeypatch.setattr('pyscaffold.termui.isatty', real_isatty)
    yield real_isatty


@pytest.fixture
def no_curses_mock():
    with disable_import('curses'):
        yield


@pytest.fixture
def curses_mock():
    with replace_import('curses', obj()):
        yield


@pytest.fixture
def no_colorama_mock():
    with disable_import('colorama'):
        yield


@pytest.fixture
def colorama_mock():
    with replace_import('colorama', obj(init=nop)):
        yield
