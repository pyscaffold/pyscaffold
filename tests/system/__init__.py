#!/usr/bin/env python
# -*- coding: utf-8 -*-
import venv
import shlex
import sys
from contextlib import contextmanager
from os import environ
from os.path import pathsep, exists
from pathlib import Path
from shutil import rmtree
from subprocess import STDOUT, check_output


def is_venv():
    """Check if the tests are running inside a venv"""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


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
        **: Any other keyword argument from :func:`subprocess.check_output`

    Returns
        str: Everything sent to the stdout and stderr by the command
    """
    args = _insert_env(normalize_run_args(args))
    opts = dict(stderr=STDOUT, universal_newlines=True)
    opts.update(kwargs)
    verbose = opts.pop('verbose', False)

    with env(opts.pop('env_vars', {})):
        if verbose:
            print(*args)
        stdout = check_output(args, **opts).strip()
        if verbose:
            print(stdout)
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
        venv.create(self.path, clear=True, with_pip=True, symlinks=True)
        # Attempt 1 to solve:
        #    self.python('-Im', 'ensurepip', '--upgrade', '--root', self.path)
        # Attempt 2 to solve:
        #    self.pip('install -U pip')
        # Attempt 3 to solve:
        #    run('curl', '-o', str(self.bin_path/"get-pip.py"),
        #        "https://bootstrap.pypa.io/get-pip.py")
        #    self.python(str(self.bin_path / "get-pip.py"))
        # Attempt 4 to solve:
        #    import ensurepip
        #    ensurepip.bootstrap(root=self.path, upgrade=True,
        #                        default_pip=True, verbosity=5)
        assert(exists(self.bin_path / 'pip'))
        # ^  This always fail -.-'
        #    For some reason, ensurepip, pip and even get-pip just skip pip
        #    installation if the python running the commands already have a pip
        #    installed alongside itself, even when `--root` or
        #    `--ignore-installed` is specified.
        #    It might be related to issue 6355 of pypa/pip
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
        args = normalize_run_args(args)
        args.insert(0, str(self.bin_path / 'python'))
        return self.run(*args, **kwargs)

    def pip(self, *args, **kwargs):
        kwargs['verbose'] = True
        args = normalize_run_args(args)
        args.insert(0, str(self.bin_path / 'pip'))
        return self.run(*args, **kwargs)

    def installed_packages(self):
        """Return the packages that were installed in this environment by pip
        """
        packages = (self.pip('freeze') or '').splitlines()
        return {
            name: version
            for name, version in (pkg.split('==') for pkg in packages)
        }


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
