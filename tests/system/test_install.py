# -*- coding: utf-8 -*-
"""Unit tests of everything related to retrieving the version

There are four tree states we want to check:
 A: sitting on the 1.0 tag
 B: dirtying the tree after 1.0
 C: a commit after a tag, clean tree
 D: a commit after a tag, dirty tree

The tests written in this file use venv to achieve isolation.
Each test will run inside a different venv in a temporary directory, so they
can execute in parallel and not interfere with each other.
"""

import inspect
import os
from contextlib import contextmanager
from glob import glob
from os.path import dirname
from os.path import join as path_join
from shutil import copyfile, rmtree, which

import pytest

from pyscaffold import shell
from pyscaffold.cli import main as putup
from pyscaffold.shell import command_exists, git
from pyscaffold.utils import chdir

from . import IS_WIN, normalize_run_args

__location__ = path_join(
    os.getcwd(),
    dirname(dirname(inspect.getfile(inspect.currentframe())))
)


pytestmark = [
    pytest.mark.slow,
    pytest.mark.system,
]


xfail_win_filename_too_long = pytest.mark.xfail(
    condition=IS_WIN,
    reason="bdist might fail on Windows because of the length limit of paths. "
           "While bdist_dumb --relative would prevent this problem for most "
           "of the cases, it seems that, there is a bug on that: "
           "https://bugs.python.org/issue993766 "
           "see #244")

untar = shell.ShellCommand(
            ("gtar" if command_exists("gtar") else "tar") + " xvzkf")
# ^ BSD tar differs in options from GNU tar,
#   so make sure to use the correct one...
#   https://xkcd.com/1168/


@pytest.fixture
def demoapp(tmpfolder, venv):
    return DemoApp(tmpfolder, venv)


@pytest.fixture
def demoapp_data(tmpfolder, venv):
    return DemoApp(tmpfolder, venv, data=True)


class DemoApp(object):
    def __init__(self, tmpdir, venv, data=None):
        self.name = 'demoapp'
        if data:
            self.name += '_data'
        self.pkg_path = path_join(str(tmpdir), self.name)
        self.built = False
        self.installed = False
        self.venv = venv
        self.data = data
        self.dist = None

        with chdir(str(tmpdir)):
            self._generate()

    def _generate(self):
        putup([self.name])
        with chdir(self.name):
            demoapp_src_dir = path_join(__location__, self.name)
            demoapp_dst_root = self.pkg_path
            demoapp_dst_pkg = path_join(demoapp_dst_root, 'src', self.name)
            copyfile(path_join(demoapp_src_dir, 'runner.py'),
                     path_join(demoapp_dst_pkg, 'runner.py'))
            git('add', path_join(demoapp_dst_pkg, 'runner.py'))
            copyfile(path_join(demoapp_src_dir, 'setup.cfg'),
                     path_join(demoapp_dst_root, 'setup.cfg'))
            copyfile(path_join(demoapp_src_dir, 'setup.py'),
                     path_join(demoapp_dst_root, 'setup.py'))
            git('add', path_join(demoapp_dst_root, 'setup.cfg'))
            git('add', path_join(demoapp_dst_root, 'setup.py'))
            if self.data:
                data_src_dir = path_join(demoapp_src_dir, 'data')
                data_dst_dir = path_join(demoapp_dst_pkg, 'data')
                os.mkdir(data_dst_dir)
                copyfile(path_join(data_src_dir, 'hello_world.txt'),
                         path_join(data_dst_dir, 'hello_world.txt'))
                git('add', path_join(data_dst_dir, 'hello_world.txt'))
            git('commit', '-m', 'Added basic application logic')

    def check_not_installed(self):
        installed = self.venv.installed_packages().keys()
        dirty = [self.name, 'UNKNOWN']
        app_list = [x for x in dirty if x in installed]
        if app_list:
            raise RuntimeError('Dirty virtual environment:\n{} found'
                               .format(', '.join(app_list)))

    def check_inside_venv(self):
        if not which(self.name, path=str(self.venv.bin_path)):
            raise RuntimeError('{} should be installed inside the venv ({})'
                               .format(self.name, self.venv.path))

    @contextmanager
    def guard(self, attr):
        if getattr(self, attr):
            raise RuntimeError(
                'For simplicity, just build/install once per package')
        yield
        setattr(self, attr, True)

    def cli(self, *args, **kwargs):
        self.check_inside_venv()
        return self.venv.run(self.name, *args, **kwargs)

    def setup_py(self, *args, **kwargs):
        with chdir(self.pkg_path):
            args = normalize_run_args(args)
            return self.venv.run('python', 'setup.py', *args, **kwargs)

    def build(self, dist='bdist'):
        with self.guard('built'), chdir(self.pkg_path):
            args = [dist]
            if 'wheel' in dist:
                self.venv.run('pip', 'install', 'wheel', verbose=True)
            if dist == 'bdist':
                args = ['bdist_dumb', '--relative']
            self.venv.run('python', 'setup.py', *args, verbose=True)
        self.dist = dist
        return self

    @property
    def dist_file(self):
        return list(glob(path_join(self.pkg_path, "dist", self.name + "*")))[0]

    def _install_bdist(self):
        with chdir(str(self.venv.path)):
            # Because of the way bdist_dumb --relative works,
            # the tar.gz will contain paths that must be extracted from inside
            # the venv
            untar(self.dist_file)

    def install(self, edit=False):
        with self.guard('installed'), chdir(self.pkg_path):
            self.check_not_installed()
            if edit or self.dist is None:
                self.venv.run('pip', 'install', '-e', '.')
            elif self.dist == 'bdist':
                self._install_bdist()
            else:
                self.venv.run('pip', 'install', self.dist_file)
        return self

    def make_dirty_tree(self):
        dirty_file = path_join(self.pkg_path, 'src', self.name, 'runner.py')
        with open(dirty_file, 'a') as fh:
            fh.write("\n\ndirty_variable = 69\n")
        return self

    def make_commit(self):
        with chdir(self.pkg_path):
            git('commit', '-a', '-m', 'message')
        return self

    def rm_git_tree(self):
        git_path = path_join(self.pkg_path, '.git')
        rmtree(git_path)
        return self

    def tag(self, name, message):
        with chdir(self.pkg_path):
            git('tag', '-a', name, '-m', message)
        return self


def check_version(output, exp_version, dirty=False):
    version = output.strip().split(' ')[-1]
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


def test_sdist_install(demoapp):
    (demoapp
        .build('sdist')
        .install())
    out = demoapp.cli('--version')
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_sdist_install_dirty(demoapp):
    (demoapp
        .tag('v0.1', 'first release')
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree()
        .build('sdist')
        .install())
    out = demoapp.cli('--version')
    exp = "0.1.post0.dev1"
    check_version(out, exp, dirty=True)


def test_sdist_install_with_1_0_tag(demoapp):
    (demoapp
        .make_dirty_tree()
        .make_commit()
        .tag('v1.0', 'final release')
        .build('sdist')
        .install())
    out = demoapp.cli('--version')
    exp = "1.0"
    check_version(out, exp, dirty=False)


def test_sdist_install_with_1_0_tag_dirty(demoapp):
    (demoapp
        .tag('v1.0', 'final release')
        .make_dirty_tree()
        .build('sdist')
        .install())
    out = demoapp.cli('--version')
    exp = "1.0"
    check_version(out, exp, dirty=True)


# bdist works like sdist so we only try one combination
@xfail_win_filename_too_long
def test_bdist_install(demoapp):
    (demoapp
        .build('bdist')
        .install())
    out = demoapp.cli('--version')
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_bdist_wheel_install(demoapp):
    (demoapp
        .build('bdist_wheel')
        .install())
    out = demoapp.cli('--version')
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_git_repo(demoapp):
    out = demoapp.setup_py('--version')
    exp = '0.0.post0.dev2'
    check_version(out, exp, dirty=False)


def test_git_repo_dirty(demoapp):
    (demoapp
        .tag('v0.1', 'first release')
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree())
    out = demoapp.setup_py('--version')
    exp = "0.1.post0.dev1"
    check_version(out, exp, dirty=True)


def test_git_repo_with_1_0_tag(demoapp):
    demoapp.tag('v1.0', 'final release')
    out = demoapp.setup_py('--version')
    exp = "1.0"
    check_version(out, exp, dirty=False)


def test_git_repo_with_1_0_tag_dirty(demoapp):
    (demoapp
        .tag('v1.0', 'final release')
        .make_dirty_tree())
    out = demoapp.setup_py('--version')
    exp = "1.0"
    check_version(out, exp, dirty=True)


def test_sdist_install_with_data(demoapp_data):
    (demoapp_data
        .build('sdist')
        .install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


@xfail_win_filename_too_long
def test_bdist_install_with_data(demoapp_data):
    (demoapp_data
        .build('bdist')
        .install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_bdist_wheel_install_with_data(demoapp_data):
    (demoapp_data
        .build('bdist_wheel')
        .install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_edit_install_with_data(demoapp_data):
    demoapp_data.install(edit=True)
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_setup_py_install_with_data(demoapp_data):
    demoapp_data.setup_py('install')
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)
    out = demoapp_data.cli('--version')
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_setup_py_develop_with_data(demoapp_data):
    demoapp_data.setup_py('develop')
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)
    out = demoapp_data.cli('--version')
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)
