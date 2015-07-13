#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkg_resources
import pyscaffold

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_version():
    version = pyscaffold.__version__.split(".")
    assert int(version[0]) >= 0


def test_unknown_version(get_distribution_raises_exception):  # noqa
    version = pyscaffold.__version__
    assert version == 'unknown'
