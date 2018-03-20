#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    Important note: Since PyScaffold is self-using and depends on
    setuptools-scm, it is important to run:
    `python setup.py egg_info --egg-base .`
    after a fresh checkout. This will generate some critically needed data.
"""
import os
import sys
import inspect
from setuptools import setup


__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

entry_points = """
[distutils.setup_keywords]
use_pyscaffold = pyscaffold.integration:pyscaffold_keyword

[console_scripts]
putup = pyscaffold.cli:run

[pyscaffold.cli]
namespace = pyscaffold.extensions.namespace:Namespace
travis = pyscaffold.extensions.travis:Travis
pre_commit = pyscaffold.extensions.pre_commit:PreCommit
tox = pyscaffold.extensions.tox:Tox
gitlab = pyscaffold.extensions.gitlab_ci:GitLab
django = pyscaffold.extensions.django:Django
cookiecutter = pyscaffold.extensions.cookiecutter:Cookiecutter
no_skeleton = pyscaffold.extensions.no_skeleton:NoSkeleton

[setuptools.file_finders]
setuptools_scm = pyscaffold.contrib.setuptools_scm.integration:find_files

[setuptools_scm.parse_scm]
.hg = pyscaffold.contrib.setuptools_scm.hg:parse
.git = pyscaffold.contrib.setuptools_scm.git:parse

[setuptools_scm.parse_scm_fallback]
.hg_archival.txt = pyscaffold.contrib.setuptools_scm.hg:parse_archival
PKG-INFO = pyscaffold.contrib.setuptools_scm.hacks:parse_pkginfo
pip-egg-info = pyscaffold.contrib.setuptools_scm.hacks:parse_pip_egg_info

[setuptools_scm.files_command]
.hg = pyscaffold.contrib.setuptools_scm.hg:FILES_COMMAND
.git = pyscaffold.contrib.setuptools_scm.git:list_files_in_archive

[setuptools_scm.version_scheme]
guess-next-dev = pyscaffold.contrib.setuptools_scm.version:guess_next_dev_version
post-release = pyscaffold.contrib.setuptools_scm.version:postrelease_version

[setuptools_scm.local_scheme]
node-and-date = pyscaffold.contrib.setuptools_scm.version:get_local_node_and_date
node-and-timestamp = pyscaffold.contrib.setuptools_scm.version:get_local_node_and_timestamp
dirty-tag = pyscaffold.contrib.setuptools_scm.version:get_local_dirty_tag
"""  # noqa


def bootstrap_cfg():
    src_dir = os.path.join(__location__, 'src')
    egg_info_dir = os.path.join(__location__, 'PyScaffold.egg-info')
    has_entrypoints = os.path.isdir(egg_info_dir)

    sys.path.insert(0, src_dir)
    from pyscaffold.utils import check_setuptools_version
    from pyscaffold.contrib.setuptools_scm import get_version
    from pyscaffold.contrib.setuptools_scm.hacks import parse_pkginfo
    from pyscaffold.contrib.setuptools_scm.git import parse as parse_git
    from pyscaffold.integration import local_version2str, version2str

    check_setuptools_version()

    def parse(root):
        try:
            return parse_pkginfo(root)
        except IOError:
            return parse_git(root)

    config = dict(
        version_scheme=version2str,
        local_scheme=local_version2str,
    )

    if has_entrypoints:
        return dict(use_pyscaffold=True)
    else:
        return dict(version=get_version(
            root=__location__, parse=parse, **config))


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    setup_args = dict(
        setup_requires=['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else [],
        entry_points=entry_points
    )
    setup_args.update(bootstrap_cfg())
    setup(**setup_args)


if __name__ == '__main__':
    setup_package()
