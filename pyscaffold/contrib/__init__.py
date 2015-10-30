# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold sourcecode itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often than
 not, see issue #71 and #72.

In order to make updating these dependencies as easy as possible the ``git
submodule`` command is used to keep those repositories inside in sync with the
upstream versions.
"""
from __future__ import division, print_function, absolute_import

import os
import sys
import inspect
from contextlib import contextmanager
from importlib import import_module

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


@contextmanager
def add_dir_to_syspath(path):
    sys.path.insert(1, path)
    try:
        yield
    finally:
        assert sys.path[1] == path
        del sys.path[1]


def import_pkg(pkg, path):
    with add_dir_to_syspath(path):
        return import_module(pkg)

pbr_path = os.path.join(__location__, 'pbr')
scm_path = os.path.join(__location__, 'setuptools_scm')
# Import contribution packages
pbr_core = import_pkg('pbr.core', pbr_path)
scm = import_pkg('setuptools_scm', scm_path)
scm_utils = import_pkg('setuptools_scm.utils', scm_path)
# Functions used by integration module
pbr_read_setup_cfg = pbr_core.pbr
scm_get_version = scm.get_version
scm_trace = scm_utils.trace
