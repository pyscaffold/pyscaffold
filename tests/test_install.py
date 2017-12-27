# -*- coding: utf-8 -*-

"""Unit tests of everything related to retrieving the version

There are four tree states we want to check:
 A: sitting on the 1.0 tag
 B: dirtying the tree after 1.0
 C: a commit after a tag, clean tree
 D: a commit after a tag, dirty tree
"""

from __future__ import absolute_import, division, print_function

import inspect
import os
import re
import shutil
import sys
from contextlib import contextmanager
from os.path import join as path_join
from os.path import exists
from shutil import copyfile, rmtree

import pytest

from pyscaffold import shell
from pyscaffold.cli import main as putup
from pyscaffold.repo import add_tag
from pyscaffold.shell import command_exists, git
from pyscaffold.utils import chdir

pytestmark = pytest.mark.slow

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


def cmd_path(cmd):
    """Try to get a fully specified command path.

    Returns the full path when possible, otherwise just the command name.
    Useful when running from virtualenv context.
    """
    candidates = os.getenv('PATH', '').split(os.pathsep)
    candidates.insert(0, path_join(sys.prefix, 'bin'))

    if hasattr(sys, 'real_prefix'):
        candidates.insert(1, path_join(getattr(sys, 'real_prefix'), 'bin'))

    for candidate in candidates:
        full_path = path_join(candidate, cmd)
        if exists(full_path):
            return full_path

    return cmd


def venv_cmd(cmd, *args):
    """Create a callable from a command inside a virtualenv."""
    return shell.ShellCommand(' '.join([cmd_path(cmd)] + list(args)))


pip = venv_cmd("pip")
setup_py = venv_cmd("python", "setup.py")
untar = shell.ShellCommand(
    ("gtar" if command_exists("gtar") else "tar") + " xvzkf")
type_ = shell.ShellCommand('file')
# ^ BSD tar differs in options from GNU tar,
#   so make sure to use the correct one...
#   https://xkcd.com/1168/


def is_inside_venv():
    return hasattr(sys, 'real_prefix')


def check_clean_venv():
    installed = [line.split()[0] for line in pip('list')]
    dirty = ['demoapp', 'demoapp_data', 'UNKNOWN']
    app_list = [x for x in dirty if x in installed]
    if not app_list:
        return
    else:
        raise RuntimeError("Dirty virtual environment:\n{} found".format(
            ', '.join(app_list)))


def create_demoapp(data=False):
    if data:
        demoapp = 'demoapp_data'
    else:
        demoapp = 'demoapp'

    putup([demoapp])
    with chdir(demoapp):
        demoapp_src_dir = os.path.join(__location__, demoapp)
        demoapp_dst_root = os.getcwd()
        demoapp_dst_pkg = os.path.join(demoapp_dst_root, 'src', demoapp)
        copyfile(os.path.join(demoapp_src_dir, 'runner.py'),
                 os.path.join(demoapp_dst_pkg, 'runner.py'))
        git('add', os.path.join(demoapp_dst_pkg, 'runner.py'))
        copyfile(os.path.join(demoapp_src_dir, 'setup.cfg'),
                 os.path.join(demoapp_dst_root, 'setup.cfg'))
        copyfile(os.path.join(demoapp_src_dir, 'setup.py'),
                 os.path.join(demoapp_dst_root, 'setup.py'))
        git('add', os.path.join(demoapp_dst_root, 'setup.cfg'))
        git('add', os.path.join(demoapp_dst_root, 'setup.py'))
        if data:
            data_src_dir = os.path.join(demoapp_src_dir, 'data')
            data_dst_dir = os.path.join(demoapp_dst_pkg, 'data')
            os.mkdir(data_dst_dir)
            copyfile(os.path.join(data_src_dir, 'hello_world.txt'),
                     os.path.join(data_dst_dir, 'hello_world.txt'))
            git('add', os.path.join(data_dst_dir, 'hello_world.txt'))
        git('commit', '-m', 'Added basic application logic')


def build_demoapp(dist, path=None, demoapp='demoapp'):
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, demoapp)
    with chdir(path):
        setup_py(dist)


@contextmanager
def installed_demoapp(dist=None, path=None, demoapp='demoapp'):
    check_clean_venv()
    if path is None:
        path = os.getcwd()
    path = os.path.join(path, demoapp, "dist", "{}*".format(demoapp))
    if dist == 'bdist':
        with chdir('/'):
            output = untar(path)
        install_dirs = list()
        install_bin = None
        for line in output:
            if re.search(r".*/site-packages/{}.*?/$".format(demoapp), line):
                install_dirs.append(line)
            if re.search(r".*/bin/{}$".format(demoapp), line):
                install_bin = line
    elif dist == 'install':
        with chdir(demoapp):
            setup_py('install')
    else:
        pip("install", path)
    try:
        yield venv_cmd(demoapp)
    finally:
        if dist == 'bdist':
            with chdir('/'):
                os.remove(install_bin)
                for path in install_dirs:
                    rmtree(path, ignore_errors=True)
        else:
            pip("uninstall", "-y", demoapp)


def check_version(output, exp_version, dirty=False):
    version = output.split(' ')[-1]
    # for some setuptools version a directory with + is generated, sometimes _
    if dirty:
        if '+' in version:
            ver, local = version.split('+')
        else:
            ver, local = version.split('_')
        assert local.endswith('dirty')
        assert ver == exp_version
    else:
        if '+' in version:
            ver = version.split('+')
        else:
            ver = version.split('_')
        if len(ver) > 1:
            assert not ver[1].endswith('dirty')
        assert ver[0] == exp_version


def make_dirty_tree(demoapp='demoapp'):
    dirty_file = os.path.join('src', demoapp, 'runner.py')
    with chdir(demoapp):
        with open(dirty_file, 'a') as fh:
            fh.write("\n\ndirty_variable = 69\n")


def make_commit(demoapp='demoapp'):
    with chdir(demoapp):
        git('commit', '-a', '-m', 'message')


def rm_git_tree(demoapp='demoapp'):
    git_path = os.path.join(demoapp, '.git')
    shutil.rmtree(git_path)


def test_sdist_install(tmpfolder):
    create_demoapp()
    build_demoapp('sdist')
    with installed_demoapp() as demoapp:
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev2"
        check_version(out, exp, dirty=False)


def test_sdist_install_dirty(tmpfolder):
    create_demoapp()
    add_tag('demoapp', 'v0.1', 'first tag')
    make_dirty_tree()
    make_commit()
    make_dirty_tree()
    build_demoapp('sdist')
    with installed_demoapp() as demoapp:
        out = next(demoapp('--version'))
        exp = "0.1.post0.dev1"
        check_version(out, exp, dirty=True)


def test_sdist_install_with_1_0_tag(tmpfolder):
    create_demoapp()
    make_dirty_tree()
    make_commit()
    add_tag('demoapp', 'v1.0', 'final release')
    build_demoapp('sdist')
    with installed_demoapp() as demoapp:
        out = next(demoapp('--version'))
        exp = "1.0"
        check_version(out, exp, dirty=False)


def test_sdist_install_with_1_0_tag_dirty(tmpfolder):
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    make_dirty_tree()
    build_demoapp('sdist')
    with installed_demoapp() as demoapp:
        out = next(demoapp('--version'))
        exp = "1.0"
        check_version(out, exp, dirty=True)


# bdist works like sdist so we only try one combination
def test_bdist_install(tmpfolder):
    create_demoapp()
    build_demoapp('bdist')
    with installed_demoapp('bdist') as demoapp:
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev2"
        check_version(out, exp, dirty=False)


# bdist wheel works like sdist so we only try one combination
@pytest.mark.skipif(not is_inside_venv(),
                    reason='Needs to run in a virtualenv')
def test_bdist_wheel_install(tmpfolder):
    create_demoapp()
    build_demoapp('bdist_wheel')
    with installed_demoapp() as demoapp:
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev2"
        check_version(out, exp, dirty=False)


def test_git_repo(tmpfolder):
    create_demoapp()
    with installed_demoapp('install'), chdir('demoapp'):
        out = next(setup_py('--version'))
        exp = '0.0.post0.dev2'
        check_version(out, exp, dirty=False)


def test_git_repo_dirty(tmpfolder):
    create_demoapp()
    add_tag('demoapp', 'v0.1', 'first tag')
    make_dirty_tree()
    make_commit()
    make_dirty_tree()
    with installed_demoapp('install'), chdir('demoapp'):
        out = next(setup_py('--version'))
        exp = '0.1.post0.dev1'
        check_version(out, exp, dirty=True)


def test_git_repo_with_1_0_tag(tmpfolder):
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    with installed_demoapp('install'), chdir('demoapp'):
        out = next(setup_py('--version'))
        exp = '1.0'
        check_version(out, exp, dirty=False)


def test_git_repo_with_1_0_tag_dirty(tmpfolder):
    create_demoapp()
    add_tag('demoapp', 'v1.0', 'final release')
    make_dirty_tree()
    with installed_demoapp('install'), chdir('demoapp'):
        out = next(setup_py('--version'))
        exp = '1.0'
        check_version(out, exp, dirty=True)


def test_sdist_install_with_data(tmpfolder):
    create_demoapp(data=True)
    build_demoapp('sdist', demoapp='demoapp_data')
    with installed_demoapp(demoapp='demoapp_data') as demoapp_data:
        out = next(demoapp_data())
        exp = "Hello World"
        assert out.startswith(exp)


def test_bdist_install_with_data(tmpfolder):
    create_demoapp(data=True)
    build_demoapp('bdist', demoapp='demoapp_data')
    with installed_demoapp('bdist', demoapp='demoapp_data') as demoapp_data:
        out = next(demoapp_data())
        exp = "Hello World"
        assert out.startswith(exp)


@pytest.mark.skipif(not is_inside_venv(),
                    reason='Needs to run in a virtualenv')
def test_bdist_wheel_install_with_data(tmpfolder):
    create_demoapp(data=True)
    build_demoapp('bdist_wheel', demoapp='demoapp_data')
    with installed_demoapp(demoapp='demoapp_data') as demoapp_data:
        out = next(demoapp_data())
        exp = "Hello World"
        assert out.startswith(exp)


def test_setup_py_install(tmpfolder):
    create_demoapp()
    with installed_demoapp('install', demoapp='demoapp') as demoapp:
        out = next(demoapp('--version'))
        exp = "0.0.post0.dev2"
        check_version(out, exp, dirty=False)
