# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold source code itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often 
than not, see issues #71 and #72.

Currently the contrib packages are:

1) setuptools_scm v3.3.3
2) pytest-runner 5.1
3) configupdater 1.0

The packages/modules were just copied over.
"""

# Following dummy definitions are here in case PyScaffold version < 3
# is still installed and setuptools checks the registered entry_points.
SCM_HG_FILES_COMMAND = ''
SCM_GIT_FILES_COMMAND = ''


def warn_about_deprecated_pyscaffold():
    raise RuntimeError("A PyScaffold version less than 3.0 was detected, "
                       "please upgrade!")


def scm_find_files(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_parse_hg(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_parse_git(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_parse_archival(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_parse_pkginfo(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_guess_next_dev_version(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_postrelease_version(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_get_local_node_and_date(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def scm_get_local_dirty_tag(*args, **kwargs):
    warn_about_deprecated_pyscaffold()


def write_pbr_json(*args, **kwargs):
    warn_about_deprecated_pyscaffold()
