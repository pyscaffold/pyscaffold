#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyscaffold

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_version():
    version = pyscaffold.__version__.split(".")
    assert int(version[0]) >= 0
