#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    Important note: Since PyScaffold is self-using and depends on
    setuptools-scm, it is important to run:
    `python setup.py egg_info --egg-base .`
    after a fresh checkout. This will generate some critically needed data.
"""
import inspect
import os
import sys

from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


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
    )
    setup_args.update(bootstrap_cfg())
    setup(**setup_args)


if __name__ == '__main__':
    setup_package()
