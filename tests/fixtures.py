#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
from shutil import rmtree

import sh
import pytest

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


@pytest.yield_fixture()
def tmpdir():
    old_path = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    os.chdir(old_path)
    rmtree(newpath)


@pytest.yield_fixture()
def git_mock():
    old_git = sh.git
    sh.git = lambda *x: True
    yield
    sh.git = old_git


@pytest.yield_fixture()
def nogit_mock():
    def raise_error():
        raise RuntimeError("No git mock!")

    old_git = sh.git
    sh.git = raise_error
    yield
    sh.git = old_git
