#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for system/integration tests"""
import shlex
import subprocess
import sys
from collections import namedtuple
from contextlib import contextmanager
from os import environ
from os.path import pathsep
from pathlib import Path
from shutil import rmtree
from textwrap import dedent


REQUIRED_VERSION = "{}.{}".format(*sys.version_info[:2])


def is_venv():
    """Check if the tests are running inside a venv"""
    return hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix)


def _global_python():
    root = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.base_prefix
    python = Path(root, 'bin', 'python' + REQUIRED_VERSION)
    return str(python) if python.exists() else sys.executable


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
            args = shlex.split(args[0])
        else:
            args = args[0]
    return list(args)


def _insert_env(args):
    """It seems that :mod:`subprocess` doesn't consider changes in the
    environment variables after the main python process is started.
    To workaround this we can always prepend the command with `env`, this
    guarantees environment variables have up-to-date values.
    """
    if len(args) > 0 and args[0] not in ("env", "/usr/bin/env"):
        args.insert(0, "/usr/bin/env")

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
    args = _insert_env(normalize_run_args(args))
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
            print(*args)
        process = subprocess.run(args, **opts)
        stdout = process.stdout.strip()
        if verbose:
            print(stdout)
        process.check_returncode()
        return stdout


class Venv:
    """High-level interface for interacting with :mod:`venv` module.

    Arguments
        path(os.PathLike): path where the venv should be created
    """
    def __init__(self, path):
        self.path = Path(path)
        self.bin_path = self.path / "bin"

    def setup(self):
        # As described in the link bellow, it is complicated to get venvs and
        # virtualenvs nested.
        # https://virtualenv.pypa.io/en/stable/reference/#compatibility-with-the-stdlib-venv-module
        # This approach is the minimal that fits our purposes:
        cmd = [_global_python(), "-Im", "venv", "--clear", str(self.path)]
        run(cmd, verbose=True)
        # Meta-test to make sure we have our own pip
        assert((self.bin_path / 'pip').exists())
        self.pip('install', '-qqq', '--upgrade', 'pip')
        # ^  this makes tests slower, comment if not needed.
        return self

    def teardown(self):
        if self.path and self.path.is_dir():
            rmtree(self.path)
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

    def python(self, *args, **kwargs):
        kwargs['verbose'] = True
        # ^   usefull for debugging, pytest hides it anyway
        args = normalize_run_args(args)
        args.insert(0, str(self.bin_path / 'python'))
        return self.run(*args, **kwargs)

    def pip(self, *args, **kwargs):
        kwargs['verbose'] = True
        # ^   usefull for debugging, pytest hides it anyway
        args = normalize_run_args(args)
        args.insert(0, str(self.bin_path / 'pip'))
        return self.run(*args, **kwargs)

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
        lines = self.python("-c", code).split('\n')
        lines = (line.strip() for line in lines)
        packages = (PackageEntry(*line.split('|')) for line in lines if line)
        return {pkg.name: pkg for pkg in packages}


def run_common_tasks(tests=True, flake8=True):
    """Run common tasks inside a PyScaffold-generated project"""
    if tests:
        run('python setup.py test')

    run('python setup.py doctest')
    run('python setup.py docs')
    run('python setup.py --version')
    run('python setup.py sdist')
    run('python setup.py bdist')

    if flake8 and environ.get('COVERAGE') == 'true':
        run('flake8 --count')
