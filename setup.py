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

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


def bootstrap_cfg():
    """Allow PyScaffold to be used to package itself.

    Usually, running ``python setup.py egg_info --egg-base .`` first is a good
    idea.
    """
    src_dir = os.path.join(__location__, "src")
    egg_info_dir = os.path.join(__location__, "PyScaffold.egg-info")
    has_entrypoints = os.path.isdir(egg_info_dir)
    import pkg_resources

    sys.path.insert(0, src_dir)
    pkg_resources.working_set.add_entry(src_dir)
    from pyscaffold.contrib.setuptools_scm import get_version
    from pyscaffold.contrib.setuptools_scm.git import parse as parse_git
    from pyscaffold.contrib.setuptools_scm.hacks import parse_pkginfo
    from pyscaffold.integration import local_version2str, version2str
    from pyscaffold.utils import check_setuptools_version

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
        return dict(version=get_version(root=__location__, parse=parse, **config))


def setup_package():
    """Call setuptools-provided `setup` using PyScaffold to bootstrap itself"""
    setup(**bootstrap_cfg())


if __name__ == "__main__":
    setup_package()
