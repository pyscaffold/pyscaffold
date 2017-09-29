# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold sourcecode itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often than
not, see issues #71 and #72.

All contribution packages were added with the help of ``git subtree`` (git
version 1.7.11 and above)::

    git subtree add --prefix pyscaffold/contrib/setuptools_scm --squash \
    https://github.com/pypa/setuptools_scm.git v1.10.1

    git subtree add --prefix pyscaffold/contrib/pbr --squash \
    https://github.com/openstack-dev/pbr.git 1.8.1

Upating works with::

    git subtree pull --prefix pyscaffold/contrib/setuptools_scm \
    https://github.com/pypa/setuptools_scm.git NEW_TAG --squash

    git subtree pull --prefix pyscaffold/contrib/pbr \
    https://github.com/openstack-dev/pbr.git NEW_TAG --squash

Using ``subtree`` instead of git's ``submodule`` had several advantages.
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
    """
    Contextmanager to temporarily prepend a path the :obj:`sys.path`

    :param path: path as string
    """
    sys.path.insert(1, path)
    try:
        yield
    finally:
        assert sys.path[1] == path
        del sys.path[1]


def import_mod(module, path):
    """
    Imports a module from a directory path

    :param module: module name as string
    :param path: path as string
    :return: module
    """
    with add_dir_to_syspath(path):
        return import_module(module)

pbr_path = os.path.join(__location__, 'pbr')
scm_path = os.path.join(__location__, 'setuptools_scm')

# Import contribution packages
pbr_json = import_mod('pbr.pbr_json', pbr_path)
pbr_core = import_mod('pbr.core', pbr_path)
scm = import_mod('setuptools_scm', scm_path)
scm_integration = import_mod('setuptools_scm.integration', scm_path)
scm_version = import_mod('setuptools_scm.version', scm_path)
scm_git = import_mod('setuptools_scm.git', scm_path)
scm_hg = import_mod('setuptools_scm.hg', scm_path)
scm_hacks = import_mod('setuptools_scm.hacks', scm_path)

# Functions used by integration module
pbr_read_setup_cfg = pbr_core.pbr
scm_get_version = scm.get_version
scm_find_files = scm_integration.find_files
scm_parse_hg = scm_hg.parse
scm_parse_git = scm_git.parse
scm_parse_archival = scm_hg.parse_archival
scm_parse_pkginfo = scm_hacks.parse_pkginfo
SCM_GIT_FILES_COMMAND = scm_git.FILES_COMMAND
SCM_GH_FILES_COMMAND = scm_hg.FILES_COMMAND
scm_guess_next_dev_version = scm_version.guess_next_dev_version
scm_postrelease_version = scm_version.postrelease_version
scm_get_local_node_and_date = scm_version.get_local_node_and_date
scm_get_local_dirty_tag = scm_version.get_local_dirty_tag
write_pbr_json = pbr_json.write_pbr_json
