#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
from shutil import rmtree

import pytest


@pytest.yield_fixture()
def tmpdir():
    old_path = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    rmtree(newpath)
    os.chdir(old_path)