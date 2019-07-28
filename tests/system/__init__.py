#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for system/integration tests"""
import shlex
import subprocess
import sys
from collections import namedtuple
from contextlib import contextmanager
from itertools import chain, product
from functools import lru_cache
from glob import iglob
from os import environ
from os.path import pathsep
from pathlib import Path
from shutil import move, rmtree, which
from textwrap import dedent

from pkg_resources import parse_version

PROJECT_DIR = environ.get(
    'TOXINIDIR',
    Path(__file__).resolve().parent.parent.parent)
COVERAGE_CONFIG = str(Path(PROJECT_DIR, '.coveragerc'))

MIN_PIP_VERSION = parse_version('19.0.0')
PYTHON_WITH_MINOR_VERSION = 'python{}.{}'.format(*sys.version_info[:2])
PYTHON_WITH_MAJOR_VERSION = 'python{}'.format(sys.version_info[0])

IS_WIN = sys.platform[:3].lower() == 'win'
BIN = 'Scripts' if IS_WIN else 'bin'
ENV = which('env') or '/usr/bin/env'
# ^  For the sake of simplifying tests, we assume that even in Windows,
#    env will be available (via msys/mingw)


def is_venv():
    """Check if the tests are running inside a venv"""
    return hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix)


@lru_cache(1)
def _global_python():
    prefix = Path(getattr(sys, 'real_prefix', sys.base_prefix))
    paths = (prefix, prefix / BIN)
    # ^  Windows can store the python executable directly under prefix
    execs = (PYTHON_WITH_MINOR_VERSION, PYTHON_WITH_MAJOR_VERSION, 'python')
    candidates = (which(e, path=str(p)) for e, p in product(execs, paths))
    return next(c for c in chain(candidates, [sys.executable]) if c)


PackageEntry = namedtuple('PackageEntry', 'name, version, source_path')


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


class Venv:
    """High-level interface for interacting with :mod:`venv` module.

    Arguments
        path(os.PathLike): path where the venv should be created
    """
    def __init__(self, path):
        self.path = Path(path)
        self.bin_path = self.path / BIN
        self._coverage_exe = False
        self.python_exe = False
        self.pip_exe = False

    def setup(self):
        # As described in the link bellow, it is complicated to get venvs and
        # virtualenvs nested.
        # https://virtualenv.pypa.io/en/stable/reference/#compatibility-with-the-stdlib-venv-module
        # This approach is the minimal that fits our purposes:
        cmd = [_global_python(), '-Im', 'venv', '--clear', self.path]
        run(cmd, verbose=True)
        # Meta-test to make sure we have our own python/pip
        self.pip_exe = which('pip', path=str(self.bin_path))
        self.python_exe = which('python', path=str(self.bin_path))
        assert self.python_exe and self.pip_exe

        if self.pip_version() < MIN_PIP_VERSION or IS_WIN:
            self.python('-m', 'pip', 'install', '--upgrade',
                        'pip', 'setuptools', 'certifi')
            # ^  this makes tests slower, so try to avoid it
            #    certifi: attempt to solve SSL errors on Windows
        return self

    def teardown(self):
        if hasattr(self, 'path') and self.path.is_dir():
            rmtree(str(self.path))
        return self

    __del__ = teardown

    def run(self, *args, **kwargs):
        old_path = kwargs.get('env_vars', environ.get('PATH'))
        env_vars = kwargs.get('env_vars', {})
        old_path = env_vars.get('PATH', environ.get('PATH'))
        env_vars['PATH'] = pathsep.join([str(self.bin_path), old_path])
        env_vars['VIRTUAL_ENV'] = str(self.path)
        kwargs['env_vars'] = env_vars
        return run(*args, **kwargs)

    def _run_prog(self, cmd, *args, **kwargs):
        kwargs.setdefault('verbose', True)
        args = normalize_run_args(args)
        return self.run(*(cmd + args), **kwargs)

    def python(self, *args, **kwargs):
        return self._run_prog([self.python_exe], *args, **kwargs)

    def pip(self, *args, **kwargs):
        return self._run_prog([self.pip_exe], *args, **kwargs)

    def pip_version(self):
        _name, version, *_localtion = self.pip('--version').split()
        return parse_version(version)

    @property
    def coverage_exe(self):
        if self._coverage_exe:
            return self._coverage_exe
        self.pip('install', 'coverage')
        self._coverage_exe = which('coverage', path=str(self.bin_path))
        assert self._coverage_exe  # Meta-test, coverage should exist
        return self._coverage_exe

    def coverage_run(self, *args, **kwargs):
        """Works as if we were invoking the ``python`` command"""
        cmd = "run --parallel-mode --rcfile".split()
        cmd = [self.coverage_exe, *cmd, COVERAGE_CONFIG]
        results = self._run_prog(cmd, *args, **kwargs)
        for fp in iglob('.coverage.*'):
            move(fp, PROJECT_DIR)
            # ^  Move to the project dir, so coverage can combine them later
        return results

    def installed_packages(self):
        """Creates a dictionary with information about the installed packages

        Function adapted from `pytest-plugins`_, under the MIT license.

        Returns:
            dict: with key as package name, and value as a namedtuple
               ``(name, version, source_path)``

        .. _pytest-plugins : https://github.com/manahl/pytest-plugins/blob/b01e0e7c00feff1895b5007edda83c29ae3eec49/pytest-fixture-config/pytest_fixture_config.py
        """  # noqa
        code = dedent("""\
           from pkg_resources import working_set
           for i in working_set:
               print(i.project_name + '|' + i.version + '|' + i.location)
        """)
        lines = self.python('-c', code).split('\n')
        lines = (line.strip() for line in lines)
        packages = (PackageEntry(*line.split('|')) for line in lines if line)
        return {pkg.name: pkg for pkg in packages}


def run_common_tasks(tests=True, flake8=True):
    """Run common tasks inside a PyScaffold-generated project"""
    if tests:
        run('python setup.py test', verbose=True)

    run('python setup.py doctest', verbose=True)
    run('python setup.py docs', verbose=True)
    run('python setup.py --version', verbose=True)
    run('python setup.py sdist', verbose=True)
    run('python setup.py bdist_dumb --relative', verbose=True)

    if flake8 and environ.get('COVERAGE') == 'true':
        run('flake8 --count', verbose=True)
