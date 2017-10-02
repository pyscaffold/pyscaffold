#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    Important note: Since PyScaffold is self-using and depends on
    setuptools-scm, it is important to run `python setup.py egg_info` after
    a fresh checkout. This will generate some critically needed data.
"""
import os
import sys
import inspect
from setuptools import setup

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

entry_points = """
[console_scripts]
putup = pyscaffold.cli:run

[pyscaffold.cli]
namespace = pyscaffold.extensions.namespace:augment_cli
travis = pyscaffold.extensions.travis:augment_cli
pre_commit = pyscaffold.extensions.pre_commit:augment_cli
tox = pyscaffold.extensions.tox:augment_cli
external_generators = pyscaffold.extensions.external_generators:augment_cli

[distutils.setup_keywords]
use_pyscaffold = pyscaffold.integration:pyscaffold_keyword

[setuptools.file_finders]
setuptools_scm = pyscaffold.contrib:scm_find_files

[setuptools_scm.parse_scm]
.hg = pyscaffold.contrib:scm_parse_hg
.git = pyscaffold.contrib:scm_parse_git

[setuptools_scm.parse_scm_fallback]
.hg_archival.txt = pyscaffold.contrib:scm_parse_archival
PKG-INFO = pyscaffold.contrib:scm_parse_pkginfo
pip-egg-info = pyscaffold.contrib:scm_parse_pip_egg_info

[setuptools_scm.files_command]
.hg = pyscaffold.contrib:SCM_HG_FILES_COMMAND
.git = pyscaffold.contrib:SCM_GIT_FILES_COMMAND

[setuptools_scm.version_scheme]
guess-next-dev = pyscaffold.contrib:scm_guess_next_dev_version
post-release = pyscaffold.contrib:scm_postrelease_version

[setuptools_scm.local_scheme]
node-and-date = pyscaffold.contrib:scm_get_local_node_and_date
dirty-tag = pyscaffold.contrib:scm_get_local_dirty_tag
"""


def bootstrap():
    egg_info = os.path.join(__location__, 'pyscaffold.egg-info')
    has_entrypoints = os.path.isdir(egg_info)

    sys.path.insert(0, os.path.join(__location__, 'src'))
    from pyscaffold.contrib import scm_parse_pkginfo
    from pyscaffold.contrib import scm_parse_git
    from pyscaffold.contrib import (
        scm_guess_next_dev_version,
        scm_get_local_node_and_date,
    )

    def parse(root):
        try:
            return scm_parse_pkginfo(root)
        except IOError:
            return scm_parse_git(root)

    config = dict(
        version_scheme=scm_guess_next_dev_version,
        local_scheme=scm_get_local_node_and_date,
    )

    if has_entrypoints:
        return dict(use_pyscaffold=True)
    else:
        from pyscaffold.contrib import scm_get_version
        return dict(version=scm_get_version(
            root=__location__, parse=parse, **config))


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup_args = dict(
        setup_requires=['six'] + sphinx,
        entry_points=entry_points
    )
    setup_args.update(bootstrap())
    setup(**setup_args)


if __name__ == '__main__':
    setup_package()
