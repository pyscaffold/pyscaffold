#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for system/integration tests"""
import shlex
import subprocess
import sys
from contextlib import contextmanager
from os import environ, getcwd
from pathlib import Path
from shutil import which
from traceback import print_exc

from pkg_resources import parse_version

from pytest_virtualenv import VirtualEnv

PROJECT_DIR = environ.get(
    'TOXINIDIR',
    Path(__file__).resolve().parent.parent.parent)

MIN_PIP_VERSION = parse_version('19.0.0')

IS_WIN = sys.platform[:3].lower() == 'win'
BIN = 'Scripts' if IS_WIN else 'bin'
ENV = which('env') or '/usr/bin/env'
# ^  For the sake of simplifying tests, we assume that even in Windows,
#    env will be available (via msys/mingw)


def is_venv():
    """Check if the tests are running inside a venv"""
    return hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix)


@contextmanager
def env(env_dict):
    original = {k: environ[k] for k in env_dict.keys() if k in environ}
    changed = [environ.putenv(k, v) or k for k, v in env_dict.items()]
    try:
        yield
    finally:
        # Restore original environment
        for k in changed:
            environ.unsetenv(k)
        for k, v in original.items():
            environ[k] = v


def normalize_run_args(args):
    """Make sure we have a flatten list of shell-words"""
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0], posix=not(IS_WIN))
        elif isinstance(args[0], (list, tuple)):
            args = args[0]

    return list(args)


def _insert_env(args):
    """It seems that :mod:`subprocess` doesn't consider changes in the
    environment variables after the main python process is started.
    To workaround this we can always prepend the command with `env`, this
    guarantees environment variables have up-to-date values.
    """
    if len(args) > 0 and args[0] not in ('env', ENV):
        args.insert(0, ENV)

    return args


def run(*args, **kwargs):
    """Run an external command (subprocess)

    Arguments
       args(str or list): list or string(s) representing the command::

            >>> run('ls -la')
            >>> run('ls', '-la')
            >>> run(['ls', '-la'])

    Keyword Arguments
        env_vars(dict): Environment variables to set while running the command
        **: Any other keyword argument from :func:`subprocess.run`

    Returns
        str: Everything sent to the stdout and stderr by the command
    """
    args = [str(a) for a in _insert_env(normalize_run_args(args))]
    opts = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    opts.update(kwargs)
    verbose = opts.pop('verbose', False)

    with env(opts.pop('env_vars', {})):
        if verbose:
            # Print command and stdout in 2 steps to provide as much
            # information as possible before an exception
            print(*args, file=sys.stderr)
        process = subprocess.run(args, **opts)
        stdout = process.stdout.strip()
        if verbose:
            print(stdout, file=sys.stderr)
        process.check_returncode()
        return stdout


class Venv(VirtualEnv):
    """High-level interface for interacting with :mod:`venv` module.

    Arguments
        path(os.PathLike): path where the venv should be created
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in environ.items():
            if 'PIP_' in k:
                self.env[k] = v
        self.path = self.virtualenv
        self.bin_path = self.path / BIN
        self.pip_exe = which('pip', path=str(self.bin_path))
        self.python_exe = which('python', path=str(self.bin_path))
        assert self.python_exe and self.pip_exe

        if self.pip_version() < MIN_PIP_VERSION or IS_WIN:
            self.run(self.python_exe, '-m', 'pip', 'install', '--upgrade',
                     'pip', 'setuptools', 'certifi')
            # ^  this makes tests slower, so try to avoid it
            #    certifi: attempt to solve SSL errors on Windows

    def run(self, *args, **kwargs):
        kwargs.setdefault('cd', getcwd())
        kwargs.setdefault('capture', True)
        verbose = kwargs.pop('verbose', True)
        args = [str(a) for a in normalize_run_args(args)]
        if verbose:
            # Print command and stdout in 2 steps to provide as much
            # information as possible before an exception
            print(*args, file=sys.stderr)
        stdout = super().run(args, **kwargs).strip()
        if verbose:
            print(stdout, file=sys.stderr)
        return stdout

    def pip_version(self):
        _name, version, *_loc = self.run(self.pip_exe, '--version').split()
        return parse_version(version)


def run_common_tasks(tests=True, flake8=True):
    """Run common tasks inside a PyScaffold-generated project"""
    if tests:
        run('python setup.py test', verbose=True)

    run('python setup.py doctest', verbose=True)
    run('python setup.py docs', verbose=True)
    run('python setup.py --version', verbose=True)
    run('python setup.py sdist', verbose=True)
    try:
        run('python setup.py bdist_dumb --relative', verbose=True)
    except:  # noqa
        if not IS_WIN:
            raise
        else:
            # bdist might fail on Windows because of the length limit of paths.
            # While bdist_dumb --relative would prevent this problem for most
            # of the cases, it seems that, there is a bug on that:
            # https://bugs.python.org/issue993766
            # see #244
            print_exc()

    if flake8 and environ.get('COVERAGE') == 'true':
        run('flake8 --count', verbose=True)
