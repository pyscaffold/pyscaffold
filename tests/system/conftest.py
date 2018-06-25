#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import os
import shlex
from glob import glob
from os.path import dirname
from os.path import join as path_join
from os.path import normpath

import pytest

from pyscaffold.utils import chdir

pytestmark = pytest.mark.slow


__location__ = path_join(os.getcwd(), dirname(
    inspect.getfile(inspect.currentframe())))


def pyscaffold_path():
    """Path to pyscaffold source code"""
    return normpath(path_join(__location__, '..', '..'))


@pytest.fixture
def venv(virtualenv, tmpdir):
    _venv = VenvWrapper(virtualenv, tmpdir)
    _venv.install_pyscaffold()
    return _venv


class VenvWrapper(object):
    """Wrap pytest-virtualenv to provide helpers for pyscaffold tests

    Args:
        venv: ``virtualenv`` fixture provided by pytest-virtualenv
        tmpdir: ``tmpdir`` fixture provided by pytest
    """

    def __init__(self, venv, tmpdir):
        self._venv = venv
        self._tmpdir = tmpdir
        self.path = str(venv.virtualenv)

    def install_pyscaffold(self):
        """Build (if not cached) and install PyScaffold"""
        with chdir(pyscaffold_path()):
            if not glob('*caffold.egg-info'):
                # As instructed in PyScaffold CONTRIBUTING guide,
                # we need to generate egg_info first
                self.run('python setup.py egg_info --egg-base .')
            dist_folder = str(self._tmpdir.mkdir('pyscaffold-dist'))
            dist = path_join(dist_folder, '*caffold*.tar.gz')
            if not glob(dist):
                self.run('python', 'setup.py', 'sdist', '-d', dist_folder)
            # TODO: use bdist_wheel in the future, when the command is made
            #       available. According with setup.cfg, this is related to a
            #       setuptools bug.
            self.run('pip', 'install', glob(dist)[0])

    def install(self, package, **kwargs):
        """Install package if missing"""
        if package not in self._venv.installed_packages():
            self._venv.install_package(package, **kwargs)

    def run(self, *args, **kwargs):
        """Run commands inside the venv"""
        # pytest-virtualenv doesn't play nicely with external os.chdir
        # so let's be explicity about it...
        kwargs['cd'] = os.getcwd()
        kwargs['capture'] = True
        # normalize args
        if len(args) == 1:
            if isinstance(args[0], str):
                args = shlex.split(args[0])
            else:
                args = args[0]
        return self._venv.run(args, **kwargs).strip()
