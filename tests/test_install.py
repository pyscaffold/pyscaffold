# -*- coding: utf-8 -*-
"""Unit tests of everything related to retrieving the version

There are four tree states we want to check:
 A: sitting on the 1.0 tag
 B: dirtying the tree after 1.0
 C: a commit after a tag, clean tree
 D: a commit after a tag, dirty tree

The tests written in this file use pytest-virtualenv to achieve isolation.
Each test will run inside a different venv in a temporary directory, so they
can execute in parallel and not interfere with each other.
"""

import inspect
import os
import shutil
from contextlib import contextmanager
from glob import glob
from os.path import join as path_join
from shutil import copyfile

import pytest

from pyscaffold import shell
from pyscaffold.cli import main as putup
from pyscaffold.shell import command_exists, git
from pyscaffold.utils import chdir

__location__ = path_join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


pytestmark = pytest.mark.slow


untar = shell.ShellCommand(("gtar" if command_exists("gtar") else "tar") + " xvzkf")
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
        self.name = "demoapp"
        if data:
            self.name += "_data"
        self.pkg_path = path_join(str(tmpdir), self.name)
        self.built = False
        self.installed = False
        self.venv = venv
        self.venv_path = str(venv.virtualenv)
        self.venv_bin = str(venv.python)
        self.data = data
        self.dist = None

        with chdir(str(tmpdir)):
            self._generate()

    def _generate(self):
        putup([self.name])
        with chdir(self.name):
            demoapp_src_dir = path_join(__location__, self.name)
            demoapp_dst_root = self.pkg_path
            demoapp_dst_pkg = path_join(demoapp_dst_root, "src", self.name)
            copyfile(
                path_join(demoapp_src_dir, "runner.py"),
                path_join(demoapp_dst_pkg, "runner.py"),
            )
            git("add", path_join(demoapp_dst_pkg, "runner.py"))
            copyfile(
                path_join(demoapp_src_dir, "setup.cfg"),
                path_join(demoapp_dst_root, "setup.cfg"),
            )
            copyfile(
                path_join(demoapp_src_dir, "setup.py"),
                path_join(demoapp_dst_root, "setup.py"),
            )
            git("add", path_join(demoapp_dst_root, "setup.cfg"))
            git("add", path_join(demoapp_dst_root, "setup.py"))
            if self.data:
                data_src_dir = path_join(demoapp_src_dir, "data")
                data_dst_dir = path_join(demoapp_dst_pkg, "data")
                os.mkdir(data_dst_dir)
                copyfile(
                    path_join(data_src_dir, "hello_world.txt"),
                    path_join(data_dst_dir, "hello_world.txt"),
                )
                git("add", path_join(data_dst_dir, "hello_world.txt"))
            git("commit", "-m", "Added basic application logic")
        # this is needed for Windows 10 which lacks some certificats
        self.run("pip", "install", "-q", "certifi")

    def check_not_installed(self):
        installed = [
            line.split()[0] for line in self.run("pip", "list").split("\n")[2:]
        ]
        dirty = [self.name, "UNKNOWN"]
        app_list = [x for x in dirty if x in installed]
        if app_list:
            raise RuntimeError(
                "Dirty virtual environment:\n%s found", ", ".join(app_list)
            )

    def check_inside_venv(self):
        # use Python tools here to avoid problem with unix/win
        cmd = "import shutil; print(shutil.which('{}'))".format(self.name)
        cmd_path = self.run("python", "-c", cmd)
        if self.venv_path not in cmd_path:
            raise RuntimeError(
                "{} found under {} should be installed inside the venv {}"
                "".format(self.name, cmd_path, self.venv_path)
            )

    @contextmanager
    def guard(self, attr):
        if getattr(self, attr):
            raise RuntimeError("For simplicity, just build/install once per package")
        yield
        setattr(self, attr, True)

    def run(self, *args, **kwargs):
        # pytest-virtualenv doesn't play nicely with external os.chdir
        # so let's be explicit about it...
        kwargs["cd"] = os.getcwd()
        kwargs["capture"] = True
        if os.name == "nt":
            # Windows 10 needs this parameter seemingly to pass env vars
            # correctly.
            kwargs["shell"] = True
        return self.venv.run(args, **kwargs).strip()

    def cli(self, *args, **kwargs):
        self.check_inside_venv()
        args = [self.name] + list(args)
        return self.run(*args, **kwargs)

    def setup_py(self, *args, **kwargs):
        with chdir(self.pkg_path):
            args = ["python", "setup.py"] + list(args)
            return self.run(*args, **kwargs)

    def build(self, dist="bdist", cli_opts=()):
        with self.guard("built"), chdir(self.pkg_path):
            if "wheel" in dist:
                self.run("pip", "install", "wheel")
            else:
                cli_opts = cli_opts or ["--format", "gztar"]
                # ^  force tar.gz (Windows defaults to zip)
            self.run("python", "setup.py", dist, *cli_opts)
        self.dist = dist
        return self

    @property
    def dist_file(self):
        return list(glob(path_join(self.pkg_path, "dist", self.name + "*")))[0]

    def _install_bdist(self):
        with chdir("/"):
            # Because of the way bdist works, the tar.gz will contain
            # the whole path to the current venv, starting from the
            # / directory ...
            untar(self.dist_file, "--force-local")
            # ^  --force-local is required to deal with Windows paths
            #    this assumes we have a GNU tar (msys or mingw can provide that but have
            #    to be prepended to PATH, since Windows seems to ship with a BSD tar)

    def install(self, edit=False):
        with self.guard("installed"), chdir(self.pkg_path):
            self.check_not_installed()
            if edit or self.dist is None:
                self.run("pip", "install", "-e", ".")
            elif self.dist == "bdist":
                self._install_bdist()
            else:
                self.run("pip", "install", self.dist_file)
        return self

    def make_dirty_tree(self):
        dirty_file = path_join(self.pkg_path, "src", self.name, "runner.py")
        with open(dirty_file, "a") as fh:
            fh.write("\n\ndirty_variable = 69\n")
        return self

    def make_commit(self):
        with chdir(self.pkg_path):
            git("commit", "-a", "-m", "message")
        return self

    def rm_git_tree(self):
        git_path = path_join(self.pkg_path, ".git")
        shutil.rmtree(git_path)
        return self

    def tag(self, name, message):
        with chdir(self.pkg_path):
            git("tag", "-a", name, "-m", message)
        return self


def check_version(output, exp_version, dirty=False):
    # if multi-line we take the last
    output = output.split("\n")[-1]
    version = output.strip().split(" ")[-1]
    # for some setuptools version a directory with + is generated, sometimes _
    if dirty:
        if "+" in version:
            ver, local = version.split("+")
        else:
            ver, local = version.split("_")
        assert local.endswith("dirty")
        assert ver == exp_version
    else:
        if "+" in version:
            ver = version.split("+")
        else:
            ver = version.split("_")
        if len(ver) > 1:
            assert not ver[1].endswith("dirty")
        assert ver[0] == exp_version


def test_sdist_install(demoapp):
    (demoapp.build("sdist").install())
    out = demoapp.cli("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_sdist_install_dirty(demoapp):
    (
        demoapp.tag("v0.1", "first release")
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree()
        .build("sdist")
        .install()
    )
    out = demoapp.cli("--version")
    exp = "0.1.post0.dev1"
    check_version(out, exp, dirty=True)


def test_sdist_install_with_1_0_tag(demoapp):
    (
        demoapp.make_dirty_tree()
        .make_commit()
        .tag("v1.0", "final release")
        .build("sdist")
        .install()
    )
    out = demoapp.cli("--version")
    exp = "1.0"
    check_version(out, exp, dirty=False)


def test_sdist_install_with_1_0_tag_dirty(demoapp):
    (demoapp.tag("v1.0", "final release").make_dirty_tree().build("sdist").install())
    out = demoapp.cli("--version")
    exp = "1.0"
    check_version(out, exp, dirty=True)


# bdist works like sdist so we only try one combination
def test_bdist_install(demoapp):
    (demoapp.build("bdist").install())
    out = demoapp.cli("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_bdist_wheel_install(demoapp):
    (demoapp.build("bdist_wheel").install())
    out = demoapp.cli("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_git_repo(demoapp):
    out = demoapp.setup_py("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_git_repo_dirty(demoapp):
    (
        demoapp.tag("v0.1", "first release")
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree()
    )
    out = demoapp.setup_py("--version")
    exp = "0.1.post0.dev1"
    check_version(out, exp, dirty=True)


def test_git_repo_with_1_0_tag(demoapp):
    demoapp.tag("v1.0", "final release")
    out = demoapp.setup_py("--version")
    exp = "1.0"
    check_version(out, exp, dirty=False)


def test_git_repo_with_1_0_tag_dirty(demoapp):
    (demoapp.tag("v1.0", "final release").make_dirty_tree())
    out = demoapp.setup_py("--version")
    exp = "1.0"
    check_version(out, exp, dirty=True)


def test_sdist_install_with_data(demoapp_data):
    (demoapp_data.build("sdist").install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_bdist_install_with_data(demoapp_data):
    (demoapp_data.build("bdist").install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_bdist_wheel_install_with_data(demoapp_data):
    (demoapp_data.build("bdist_wheel").install())
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_edit_install_with_data(demoapp_data):
    demoapp_data.install(edit=True)
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_setup_py_install_with_data(demoapp_data):
    demoapp_data.setup_py("install")
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)
    out = demoapp_data.cli("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)


def test_setup_py_develop_with_data(demoapp_data):
    demoapp_data.setup_py("develop")
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)
    out = demoapp_data.cli("--version")
    exp = "0.0.post0.dev2"
    check_version(out, exp, dirty=False)
