# -*- coding: utf-8 -*-
import builtins
import logging
import os
import shlex
import stat
import sys
from collections import namedtuple
from contextlib import contextmanager
from distutils.util import strtobool
from importlib import reload
from importlib.util import find_spec
from os import environ
from os.path import isdir
from os.path import join as path_join
from shutil import rmtree, which

from pkg_resources import DistributionNotFound

import pytest

from .helpers import uniqstr


def nop(*args, **kwargs):
    """Function that does nothing"""


def obj(**kwargs):
    """Create a generic object with the given fields"""
    constructor = namedtuple("GenericObject", kwargs.keys())
    return constructor(**kwargs)


def set_writable(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise RuntimeError


def command_exception(content):
    # Be lazy to import modules, so coverage has time to setup all the
    # required "probes"
    # (see @FlorianWilhelm comments on #174)
    from pyscaffold.exceptions import ShellCommandException

    return ShellCommandException(content)


@pytest.fixture
def venv():
    """Create a virtualenv for each test"""
    from pytest_virtualenv import VirtualEnv

    virtualenv = VirtualEnv()
    return virtualenv


@pytest.fixture
def venv_run(venv):
    """Run a command inside the venv"""

    class Functor(object):
        def __init__(self):
            self.venv = venv

        def __call__(self, *args, **kwargs):
            # pytest-virtualenv doesn't play nicely with external os.chdir
            # so let's be explicit about it...
            kwargs["cd"] = os.getcwd()
            kwargs["capture"] = True
            if len(args) == 1 and isinstance(args[0], str):
                args = shlex.split(args[0])
            return self.venv.run(args, **kwargs).strip()

    return Functor()


@pytest.fixture
def venv_path(venv):
    return str(venv.virtualenv)


@pytest.fixture
def pyscaffold():
    return __import__("pyscaffold")


@pytest.fixture
def real_isatty():
    pyscaffold = __import__("pyscaffold", globals(), locals(), ["termui"])
    return pyscaffold.termui.isatty


@pytest.fixture
def logger():
    pyscaffold = __import__("pyscaffold", globals(), locals(), ["log"])
    return pyscaffold.log.logger


@pytest.fixture
def with_coverage():
    return strtobool(os.environ.get("COVERAGE", "NO"))


@pytest.fixture(autouse=True)
def isolated_logger(request, logger):
    # In Python the common idiom of using logging is to share the same log
    # globally, even between threads. While this is usually OK because
    # internally Python takes care of locking the shared resources, it also
    # makes very difficult to build things on top of the logging system without
    # using the same global approach.
    # For simplicity, to make things easier to extension developers and because
    # PyScaffold not really uses multiple threads, this is the case in
    # `pyscaffold.log`.
    # On the other hand, shared state and streams can make the testing
    # environment a real pain, since we are messing with everything all the
    # time, specially when running tests in parallel (so we not guarantee the
    # execution order).
    # This fixture do a huge effort in trying to isolate as much as possible
    # each test function regarding logging. We keep the global object, so the
    # tests can be seamless, but internally replace the underlying native
    # loggers and handlers for "one-shot" ones.
    # (Of course, we can keep the same global object just because the plugins
    # for running tests in parallel are based in multiple processes instead of
    # threads, otherwise we would need another strategy)

    if "original_logger" in request.keywords:
        # Some tests need to check the original implementation to make sure
        # side effects of the shared object are consistent. We have to try to
        # make them as few as possible.
        yield
        return

    # Get a fresh new logger, not used anywhere
    raw_logger = logging.getLogger(uniqstr())
    # ^  Python docs advert against instantiating Loggers directly and instruct
    #    devs to use `getLogger`. So we use a unique name to guarantee we get a
    #    new logger each time.
    raw_logger.setLevel(logging.NOTSET)
    new_handler = logging.StreamHandler()

    # Replace the internals of the LogAdapter
    # --> Messing with global state: don't try this at home ...
    #     (if we start to use threads, we cannot do this)
    old_handler = logger.handler
    old_formatter = logger.formatter
    old_wrapped = logger.wrapped
    old_nesting = logger.nesting

    # Be lazy to import modules due to coverage warnings
    # (see @FlorianWilhelm comments on #174)
    from pyscaffold.log import ReportFormatter

    logger.wrapped = raw_logger
    logger.handler = new_handler
    logger.formatter = ReportFormatter()
    logger.handler.setFormatter(logger.formatter)
    logger.wrapped.addHandler(logger.handler)
    logger.nesting = 0
    # <--

    try:
        yield
    finally:
        logger.hanlder = old_handler
        logger.formatter = old_formatter
        logger.wrapped = old_wrapped
        logger.nesting = old_nesting

        new_handler.close()
        # ^  Force the handler to not be re-used


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
        cmd = " ".join(["git"] + list(args))

        if kwargs.get("log", False):
            logger.report("run", cmd, context=os.getcwd())

        def _response():
            yield "git@mock"

        return _response()

    def _is_git_repo(folder):
        return isdir(path_join(folder, ".git"))

    monkeypatch.setattr("pyscaffold.shell.git", _git)
    monkeypatch.setattr("pyscaffold.repo.is_git_repo", _is_git_repo)

    yield _git


@pytest.fixture
def nogit_mock(monkeypatch):
    def raise_error(*_):
        raise command_exception("No git mock!")

    monkeypatch.setattr("pyscaffold.shell.git", raise_error)
    yield


@pytest.fixture
def nonegit_mock(monkeypatch):
    monkeypatch.setattr("pyscaffold.shell.git", None)
    yield


@pytest.fixture
def noconfgit_mock(monkeypatch):
    def raise_error(*argv):
        if "config" in argv:
            raise command_exception("No git mock!")

    monkeypatch.setattr("pyscaffold.shell.git", raise_error)
    yield


@pytest.fixture
def nodjango_admin_mock(monkeypatch):
    def raise_error(*_):
        raise command_exception("No django_admin mock!")

    monkeypatch.setattr("pyscaffold.shell.django_admin", raise_error)
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
    with disable_import("cookiecutter"):
        yield


@pytest.fixture
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

    tmpfolder.mkdir("custom-cookiecutters")
    tmpfolder.mkdir("cookiecutters-replay")

    config_file = tmpfolder.join("cookiecutter.yaml")
    config_file.write(config)
    environ["COOKIECUTTER_CONFIG"] = str(config_file)

    yield

    del environ["COOKIECUTTER_CONFIG"]


@pytest.fixture
def old_setuptools_mock():
    class OldSetuptools(object):
        __version__ = "10.0.0"

    with replace_import("setuptools", OldSetuptools):
        yield


@pytest.fixture
def nosphinx_mock():
    with disable_import("sphinx"):
        yield


@pytest.fixture
def get_distribution_raises_exception(monkeypatch, pyscaffold):
    def raise_exeception(name):
        raise DistributionNotFound("No get_distribution mock")

    monkeypatch.setattr("pkg_resources.get_distribution", raise_exeception)
    reload(pyscaffold)
    try:
        yield
    finally:
        monkeypatch.undo()
        reload(pyscaffold)


@pytest.fixture(autouse=True)
def no_isatty(monkeypatch, real_isatty):
    # Requiring real_isatty ensures processing that fixture
    # before this one. Therefore real_isatty is cached before the mock
    # replaces the real function.

    # Avoid ansi codes in tests, since capture fixtures seems to
    # emulate stdout and stdin behavior (including isatty method)
    monkeypatch.setattr("pyscaffold.termui.isatty", lambda *_: False)
    yield


@pytest.fixture
def orig_isatty(monkeypatch, real_isatty):
    monkeypatch.setattr("pyscaffold.termui.isatty", real_isatty)
    yield real_isatty


@pytest.fixture
def no_curses_mock():
    with disable_import("curses"):
        yield


@pytest.fixture
def curses_mock():
    with replace_import("curses", obj()):
        yield


@pytest.fixture
def no_colorama_mock():
    with disable_import("colorama"):
        yield


@pytest.fixture
def colorama_mock():
    with replace_import("colorama", obj(init=nop)):
        yield


@pytest.fixture
def tox():
    if sys.platform == "win32":
        pytest.skip("Windows tests don't play nicely with nested tox")
    elif which("tox"):
        yield "tox"
    elif find_spec("tox"):
        yield "{} -m tox".format(sys.executable)
    else:
        pytest.skip("For some reason tox cannot be found.")
