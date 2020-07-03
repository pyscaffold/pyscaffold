# -*- coding: utf-8 -*-

import pyscaffold


def test_version():
    version = pyscaffold.__version__.split(".")
    assert int(version[0]) >= 0


def test_unknown_version(get_distribution_raises_exception):
    version = pyscaffold.__version__
    assert version == "unknown"
