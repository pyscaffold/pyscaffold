#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for system/integration tests"""
import shlex
import subprocess
import sys
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache
from os import environ
from os.path import pathsep, exists
from pathlib import Path
from shutil import rmtree
from textwrap import dedent


def is_venv():
    """Check if the tests are running inside a venv"""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


@lru_cache(maxsize=1)
def global_python():
    minor_version = "{}.{}".format(*sys.version_info[:2])
    major_version = "{}".format(sys.version[0])
    possible_python = [
        '/usr/local/bin/python{}'.format(minor_version),
        '/usr/bin/python{}'.format(minor_version),
        '/bin/python{}'.format(minor_version),
        '/usr/local/bin/python{}'.format(major_version),
        '/usr/bin/python{}'.format(major_version),
        '/bin/python{}'.format(major_version),
    ]
    travis_dir = environ.get('TRAVIS_BUILD_DIR')
    if travis_dir:
        conda_python = str(Path(travis_dir) / '.venv/bin/python')
        possible_python.insert(0, conda_python)
    return next((p for p in possible_python if exists(p)), None)


@lru_cache(maxsize=1)
def venv_is_globally_available():
    possible_python = global_python()
    if possible_python is None:
        return False

    process = subprocess.run([possible_python, '-c', 'import venv'])
    return process.returncode == 0


class ImpossibleToCreateVenv(RuntimeError):
    """Preconditions to create a venv are not met"""


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

    def __del__(self):
        if self.path and self.path.is_dir():
            rmtree(self.path)

    def setup(self):
        # TODO: Use one of the following as soon as the misterious
        #       pip/ensurepip bug for nested venvs is fixed.
        #
        # import venv
        # venv.create(self.path, clear=True, with_pip=True, symlinks=True)
        # # Attempt 1:
        #    self.python('-Im', 'ensurepip', '--upgrade', '--root', self.path)
        # # Attempt 2:
        #    self.pip('install -U pip')
        # # Attempt 3:
        #    run('curl', '-o', str(self.bin_path/"get-pip.py"),
        #        "https://bootstrap.pypa.io/get-pip.py")
        #    self.python(str(self.bin_path / "get-pip.py"))
        # # Attempt 4:
        #    import ensurepip
        #    ensurepip.bootstrap(root=self.path, upgrade=True,
        #                        default_pip=True, verbosity=5)
        # assert(exists(self.bin_path / 'pip'))
        # ^  This always fail -.-'
        #    For some reason, ensurepip, pip and even get-pip just skip pip
        #    installation if the python running the commands already have a pip
        #    installed alongside itself, even when `--root` or
        #    `--ignore-installed` is specified.
        #    It might be related to issue 6355 of pypa/pip

        # FOR NOW:
        # Try to use the system's default python, so we avoid the problems
        # above described.
        python_exec = global_python() or sys.executable
        if python_exec is None:
            raise ImpossibleToCreateVenv("python3 executable not found")

        try:
            cmd = [python_exec, "-Im", "venv", "--clear", str(self.path)]
            run(cmd, verbose=True)
        except Exception as ex:
            raise ImpossibleToCreateVenv from ex

        # Meta-test to make sure we have our own pip
        assert(exists(self.bin_path / 'pip'))
        # self.run(str(self.bin_path / 'pip'), 'install', '--upgrade', 'pip')
        # ^  let's remove it for now, to speed-up tests. Uncomment if needed.
        return self

    def teardown(self):
        rmtree(self.path)
        return self

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
