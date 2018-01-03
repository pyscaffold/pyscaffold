# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold source code itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often 
than not, see issues #71 and #72.

Currently the contrib packages are:

1) setuptools_scm v1.15.6
2) six 1.11.0
3) pytest-runner 3.0

The packages/modules were just copied over.
"""
from __future__ import division, print_function, absolute_import


# Following dummy definitions are here in case PyScaffold version < 3
# is still installed and setuptools checks the registered entry_points.
SCM_HG_FILES_COMMAND = None
SCM_GIT_FILES_COMMAND = None


def scm_find_files():
    pass


def scm_parse_hg():
    pass


def scm_parse_git():
    pass


def scm_parse_archival():
    pass


def scm_parse_pkginfo():
    pass


def scm_guess_next_dev_version():
    pass


def scm_postrelease_version():
    pass


def scm_get_local_node_and_date():
    pass


def scm_get_local_dirty_tag():
    pass


def write_pbr_json():
    pass
