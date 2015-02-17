# -*- coding: utf-8 -*-

"""Unit tests of everything related to retrieving the version

There are four tree states we want to check:
 SA: sitting on the 1.0 tag
 SB: dirtying the tree after 1.0
 SC: a commit after a tag, clean tree
 SD: a commit after a tag, dirty tree

Then we're interested in 5 kinds of trees:
 TA: source tree (with .git)
 TB: source tree without .git (should get 'unknown')
 TC: source tree without .git unpacked into prefixdir
 TD: git-archive tarball
 TE: unpacked sdist tarball

In three runtime situations:
 RA1: setup.py --version
 RA2: ...path/to/setup.py --version (from outside the source tree)
 RB: setup.py sdist/bdist/bdist_wheel; pip install dist; rundemo --version

We can only detect dirty files in real git trees, so we don't examine
SB for TB/TC/TD/TE, or RB.
"""

from __future__ import absolute_import, division, print_function

import inspect
import os
import re
import sys
from contextlib import contextmanager
from shutil import copyfile, rmtree

import pytest
from pyscaffold import shell
from pyscaffold.repo import add_tag
from pyscaffold.runner import main as putup
from pyscaffold.shell import git
from pyscaffold.utils import chdir

from .fixtures import tmpdir  # noqa

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


pip = shell.Command("pip")
setup_py = shell.Command("python setup.py")
demoapp = shell.Command("demoapp")
untar = shell.Command("tar xvfzk")


def is_inside_venv():
    return hasattr(sys, 'real_prefix')


def create_demoapp():
    putup(['demoapp'])
    with chdir('demoapp'):
        demoapp_src_dir = os.path.join(__location__, 'demoapp')
        demoapp_dst_dir = os.path.join(os.getcwd(), 'demoapp')
        copyfile(os.path.join(demoapp_src_dir, 'runner.py'),
                 os.path.join(demoapp_dst_dir, 'runner.py'))
        git('add', os.path.join(demoapp_dst_dir, 'runner.py'))
        demoapp_dst_dir = os.getcwd()
        copyfile(os.path.join(demoapp_src_dir, 'setup.cfg'),
                 os.path.join(demoapp_dst_dir, 'setup.cfg'))
        git('add', os.path.join(demoapp_dst_dir, 'setup.cfg'))
        git('commit', '-m', 'Added basic progamme logic')


def build_demoapp(dist, path=None):
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, "demoapp")
    with chdir(path):
        if dist == 'git_archive':
            os.mkdir('dist')
            filename = os.path.join('dist', 'demoapp.tar.gz')
            git('archive', '--format', 'tar.gz', '--output', filename,
                '--prefix', 'demoapp_unpacked/', 'HEAD')
        else:
            setup_py(dist)


@contextmanager
def installed_demoapp(dist=None, path=None):
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, "demoapp", "dist", "demoapp*")
    if dist == 'bdist':
        with chdir('/'):
            output = untar(path)
        install_dirs = list()
        install_bin = None
        for line in output:
            if re.search(r".*/site-packages/demoapp.*?/$", line):
                install_dirs.append(line)
            if re.search(r".*/bin/demoapp$", line):
                install_bin = line
    else:
        pip("install", path)
    try:
        yield
    finally:
        if dist == 'bdist':
            with chdir('/'):
                os.remove(install_bin)
                for path in install_dirs:
                    rmtree(path, ignore_errors=True)
        else:
            pip("uninstall", "-y", "demoapp")


def check_version(output, exp_version, dirty=False):
    if dirty:
        ver, local = output.split(' ')[1].split('+')
        assert local.endswith('dirty')
        assert ver == exp_version
    else:
        ver = output.split(' ')[1].split('+')
        if len(ver) > 1:
            assert not ver[1].endswith('dirty')
        assert ver[0] == exp_version


def make_dirty_tree():
    dirty_file = os.path.join('demoapp', 'runner.py')
    with chdir('demoapp'):
        with open(dirty_file, 'a') as fh:
            fh.write("\n\ndirty_variable = 69\n")


def test_sdist_install(tmpdir):  # noqa
    create_demoapp()
    build_demoapp('sdist')
    with installed_demoapp():
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev1"
        check_version(out, exp, dirty=False)


def test_sdist_install_dirty(tmpdir):  # noqa
    create_demoapp()
    make_dirty_tree()
    build_demoapp('sdist')
    with installed_demoapp():
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev1"
        check_version(out, exp, dirty=True)


def test_sdist_install_with_1_0_tag(tmpdir):  # noqa
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    build_demoapp('sdist')
    with installed_demoapp():
        out = next(demoapp('--version'))
        exp = "1.0"
        check_version(out, exp, dirty=False)


def test_sdist_install_with_1_0_tag_dirty(tmpdir):  # noqa
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    make_dirty_tree()
    build_demoapp('sdist')
    with installed_demoapp():
        out = next(demoapp('--version'))
        exp = "1.0"
        check_version(out, exp, dirty=True)


def test_bdist_install(tmpdir):  # noqa
    create_demoapp()
    build_demoapp('bdist')
    with installed_demoapp('bdist'):
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev1"
        check_version(out, exp, dirty=False)


@pytest.mark.skipif(not is_inside_venv(),  # noqa
                    reason='Needs to run in a virtualenv')
def test_bdist_wheel_install(tmpdir):
    create_demoapp()
    build_demoapp('bdist_wheel')
    with installed_demoapp():
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev1"
        check_version(out, exp, dirty=False)


def test_git_archive(tmpdir):  # noqa
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    build_demoapp('git_archive')
    untar(os.path.join('demoapp', 'dist', 'demoapp.tar.gz'))
    with chdir('demoapp_unpacked'):
        out = list(setup_py('version'))[-1]
        exp = '1.0'
        check_version(out, exp, dirty=False)
