"""Unit tests of everything related to retrieving the version

There are four tree states we want to check:
 A: sitting on the 1.0 tag
 B: dirtying the tree after 1.0
 C: a commit after a tag, clean tree
 D: a commit after a tag, dirty tree

Each test will run inside a different venv in a temporary directory, so they
can execute in parallel and not interfere with each other.
"""

import os
import shutil
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile

import pytest

from pyscaffold import shell
from pyscaffold.cli import main as putup
from pyscaffold.extensions import venv
from pyscaffold.file_system import chdir
from pyscaffold.shell import git

__location__ = Path(__file__).parent


pytestmark = pytest.mark.slow


@pytest.fixture
def demoapp(tmpfolder):
    app = DemoApp(tmpfolder)
    with chdir(app.pkg_path):
        yield app


@pytest.fixture
def demoapp_data(tmpfolder):
    app = DemoApp(tmpfolder, data=True)
    with chdir(app.pkg_path):
        yield app


class DemoApp:
    def __init__(self, tmpdir, data=None):
        self.name = "demoapp"
        if data:
            self.name += "_data"
        self.pkg_path = Path(str(tmpdir), self.name)
        self.built = False
        self.installed = False

        self.venv_path = Path(str(tmpdir), ".venv")
        venv.create(self.venv_path)
        assert self.venv_path.exists()

        self._cmd_opts = {
            "shell": os.name == "nt",  # needed on Windows to pass env vars correctly.
            "include_path": False,  # avoid leaking executables outside the venv
        }
        self.python = shell.get_command("python", self.venv_path, **self._cmd_opts)
        # ^ Python inside the venv...
        #   Different from ``shell.python`` which is the one running the tests (.tox)
        self._cli = None

        self.data = data
        self.dist = None

        with chdir(str(tmpdir)):
            self._generate()

    def _generate(self):
        putup([self.name])
        with chdir(self.name):
            demoapp_src_dir = __location__ / self.name
            demoapp_dst_root = self.pkg_path
            demoapp_dst_pkg = demoapp_dst_root / "src" / self.name
            copyfile(demoapp_src_dir / "runner.py", demoapp_dst_pkg / "runner.py")
            git("add", demoapp_dst_pkg / "runner.py")
            for file in "setup.cfg setup.py pyproject.toml".split():
                copyfile(demoapp_src_dir / file, demoapp_dst_root / file)
                git("add", demoapp_dst_root / file)
            if self.data:
                data_src_dir = demoapp_src_dir / "data"
                data_dst_dir = demoapp_dst_pkg / "data"
                os.mkdir(data_dst_dir)
                pkg_file = data_dst_dir / "__init__.py"
                pkg_file.write_text("")
                git("add", pkg_file)
                for file in "hello_world.txt".split():
                    copyfile(data_src_dir / file, data_dst_dir / file)
                    git("add", data_dst_dir / file)
            git("commit", "-m", "Added basic application logic")

        # setuptools-scm is used for tests
        if os.name == "os":
            # Windows lacks some certificates
            self.pip("install", "-q", "certifi", "setuptools_scm")
        else:
            self.pip("install", "-q", "setuptools_scm")

    def pip(self, *cmd, **kwargs):
        return self.python("-m", "pip", *cmd, **kwargs)

    def check_not_installed(self):
        installed = [line.split()[0] for line in list(self.pip("list"))[2:]]
        dirty = [self.name, "UNKNOWN"]
        app_list = [x for x in dirty if x in installed]
        if app_list:
            msg = f"Dirty virtual environment:\n{', '.join(app_list)} found"
            raise RuntimeError(msg)

    @contextmanager
    def guard(self, attr):
        if getattr(self, attr):
            raise RuntimeError("For simplicity, just build/install once per package")
        yield
        setattr(self, attr, True)

    @property
    def cli(self):
        if self._cli is None:
            self._cli = shell.get_command(self.name, self.venv_path, **self._cmd_opts)
        return self._cli

    def get_version(self):
        out = "".join(self.cli("--version"))
        return out.replace(self.name, "").strip()

    def build(self, dist="wheel", cli_opts=()):
        with self.guard("built"), chdir(self.pkg_path):
            # For the sake of speed, we use the same Python running the tests
            # (inside .tox) and skip isolation (no extra venv just for building)
            args = [self.pkg_path, *cli_opts]
            shell.python("-m", "build", "--no-isolation", f"--{dist}", *args)
        self.dist = dist
        return self

    @property
    def dist_file(self):
        return next((self.pkg_path / "dist").glob(self.name + "*"))

    def install(self, edit=False):
        with self.guard("installed"), chdir(self.pkg_path):
            self.check_not_installed()
            if edit or self.dist is None:
                self.pip("install", "-e", ".")
            else:
                self.pip("install", self.dist_file)
        return self

    def installed_path(self):
        if not self.installed:
            return None

        cmd = f"import {self.name}; print({self.name}.__path__[0])"
        return Path(next(self.python("-c", cmd)))

    def make_dirty_tree(self):
        dirty_file = self.pkg_path / "src" / self.name / "runner.py"
        with open(dirty_file, "a") as fh:
            fh.write("\n\ndirty_variable = 69\n")
        return self

    def make_commit(self):
        with chdir(self.pkg_path):
            git("commit", "-a", "-m", "message")
        return self

    def rm_git_tree(self):
        git_path = self.pkg_path / ".git"
        shutil.rmtree(git_path)
        return self

    def tag(self, name, message):
        with chdir(self.pkg_path):
            git("tag", "-a", name, "-m", message)
        return self


def check_version(version, exp_version, dirty=False):
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    dirty_tag = f".d{today}"
    # ^  this depends on the local strategy configured for setuptools_scm...
    #    the default 'node-and-date'

    sep = "+" if "+" in version else "_"
    # ^  for some setuptools version a directory with + is generated, sometimes _

    if dirty:
        ver, local = version.split(sep)
        assert local.endswith(dirty_tag)
        assert ver == exp_version
    else:
        ver = version.split(sep)
        if len(ver) > 1:
            assert not ver[1].endswith(dirty_tag)
        assert ver[0] == exp_version


def test_sdist_install(demoapp):
    (demoapp.build("sdist").install())
    exp = "0.0.post1.dev2"
    check_version(demoapp.get_version(), exp, dirty=False)


def test_sdist_install_dirty(demoapp):
    (
        demoapp.tag("v0.1", "first release")
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree()
        .build("sdist")
        .install()
    )
    exp = "0.1.post1.dev1"
    check_version(demoapp.get_version(), exp, dirty=True)


def test_sdist_install_with_1_0_tag(demoapp):
    (
        demoapp.make_dirty_tree()
        .make_commit()
        .tag("v1.0", "final release")
        .build("sdist")
        .install()
    )
    exp = "1.0"
    check_version(demoapp.get_version(), exp, dirty=False)


def test_sdist_install_with_1_0_tag_dirty(demoapp):
    demoapp.tag("v1.0", "final release").make_dirty_tree().build("sdist").install()
    exp = "1.0.post1.dev0"
    check_version(demoapp.get_version(), exp, dirty=True)


def test_wheel_install(demoapp):
    demoapp.build("wheel").install()
    exp = "0.0.post1.dev2"
    check_version(demoapp.get_version(), exp, dirty=False)


def test_sdist_install_with_data(demoapp_data):
    demoapp_data.build("sdist").install()
    out = "".join(demoapp_data.cli())
    exp = "Hello World"
    assert out.startswith(exp)


def test_wheel_install_with_data(demoapp_data):
    demoapp_data.build("wheel").install()
    path = demoapp_data.installed_path()
    assert path.exists()
    assert (path / "data/__init__.py").exists()
    assert (path / "data/hello_world.txt").exists()
    assert (path / "runner.py").exists()
    out = "".join(demoapp_data.cli())
    exp = "Hello World"
    assert out.startswith(exp)


def test_edit_install_with_data(demoapp_data):
    demoapp_data.install(edit=True)
    out = "".join(demoapp_data.cli())
    exp = "Hello World"
    assert out.startswith(exp)
