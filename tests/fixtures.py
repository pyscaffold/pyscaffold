#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
from shutil import rmtree

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