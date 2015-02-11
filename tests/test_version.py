# -*- coding: utf-8 -*-

"""Unit tests of everything related to retrieving the version

There are three tree states we're interested in:
 SA: sitting on the 1.0 tag
 SB: dirtying the tree after 1.0
 SC: making a new commit after 1.0, clean tree

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
from shutil import copyfile

from pyscaffold import shell
from pyscaffold.runner import main as putup
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
untar = shell.Command("tar xvfz")


def create_demoapp():
    putup(['demoapp'])
    with chdir('demoapp'):
        demoapp_src_dir = os.path.join(__location__, 'demoapp')
        demoapp_dst_dir = os.path.join(os.getcwd(), 'demoapp')
        copyfile(os.path.join(demoapp_src_dir, 'runner.py'),
                 os.path.join(demoapp_dst_dir, 'runner.py'))
        shell.git('add', os.path.join(demoapp_dst_dir, 'runner.py'))
        demoapp_dst_dir = os.getcwd()
        copyfile(os.path.join(demoapp_src_dir, 'setup.cfg'),
                 os.path.join(demoapp_dst_dir, 'setup.cfg'))
        shell.git('add', os.path.join(demoapp_dst_dir, 'setup.cfg'))
        shell.git('commit', '-m', 'Added basic progamme logic')


def build_demoapp(dist, path=None):
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, "demoapp")
    with chdir(path):
        setup_py(dist)


def install_demoapp(dist=None, path=None):
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, "demoapp", "dist", "demoapp*")
    if dist == 'bdist':
        with chdir('./'):
            untar(path)
    else:
        pip("install", path)


def uninstall_demoapp():
    pip("uninstall", "demoapp")


def check_version(output, exp_version, dirty=False):
    ver = output.split(' ')[1].split('+')[0]
    assert ver == exp_version


def test_sdist_install(tmpdir):  # noqa
    create_demoapp()
    build_demoapp('sdist')
    install_demoapp()
    out = next(demoapp('--version'))
    exp = "0.0.post0.dev1"
    check_version(out, exp, dirty=False)


def test_bdist_install(tmpdir):  # noqa
    create_demoapp()
    build_demoapp('bdist')
    install_demoapp('bdist')
    out = next(demoapp('--version'))
    exp = "0.0.post0.dev1"
    check_version(out, exp, dirty=False)


def test_bdist_wheel_install(tmpdir):  # noqa
    create_demoapp()
    build_demoapp('bdist_wheel')
    install_demoapp()
    out = next(demoapp('--version'))
    exp = "0.0.post0.dev1"
    check_version(out, exp, dirty=False)
