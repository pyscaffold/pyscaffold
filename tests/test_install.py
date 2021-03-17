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

import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from shutil import copyfile
from time import strftime

import pytest

from pyscaffold import dependencies as deps
from pyscaffold import info, shell
from pyscaffold.cli import main as putup
from pyscaffold.file_system import chdir
from pyscaffold.shell import command_exists, git

__location__ = Path(__file__).parent


pytestmark = pytest.mark.slow


untar = shell.ShellCommand(("gtar" if command_exists("gtar") else "tar") + " xvzkf")
# ^ BSD tar differs in options from GNU tar, so make sure to use the correct one...
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
        self.pkg_path = Path(str(tmpdir), self.name)
        self.built = False
        self.installed = False
        self.venv = venv
        self.venv_path = Path(str(venv.virtualenv))
        self.venv_bin = Path(str(venv.python))
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
        # this is needed for Windows 10 which lacks some certificates
        self.run("pip", "install", "-q", "certifi")

    def check_not_installed(self):
        installed = [
            line.split()[0] for line in self.run("pip", "list").split("\n")[2:]
        ]
        dirty = [self.name, "UNKNOWN"]
        app_list = [x for x in dirty if x in installed]
        if app_list:
            raise RuntimeError(
                f"Dirty virtual environment:\n{', '.join(app_list)} found"
            )

    def check_inside_venv(self):
        # use Python tools here to avoid problem with unix/win
        cmd = f"import shutil; print(shutil.which('{self.name}'))"
        cmd_path = self.run("python", "-c", cmd)
        if str(self.venv_path) not in cmd_path:
            raise RuntimeError(
                f"{self.name} found under {cmd_path} should be installed inside the "
                f"venv {self.venv_path}"
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
            args = ["python", "-Wignore", "setup.py"] + list(args)
            # Avoid warnings since we are going to compare outputs
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
        return list((self.pkg_path / "dist").glob(self.name + "*"))[0]

    def _install_bdist(self):
        setupcfg = info.read_setupcfg(self.pkg_path)
        requirements = deps.split(setupcfg["options"]["install_requires"].value)
        self.run("pip", "install", *requirements)
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

    def installed_path(self):
        if not self.installed:
            return None

        cmd = f"import {self.name}; print({self.name}.__path__[0])"
        return Path(self.run("python", "-c", cmd))

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


def check_version(output, exp_version, dirty=False):
    # if multi-line we take the last
    output = output.split("\n")[-1]
    version = output.strip().split(" ")[-1]
    dirty_tag = ".d" + strftime("%Y%m%d")
    # ^  this depends on the local strategy configured for setuptools_scm...
    #    the default 'node-and-date'

    # for some setuptools version a directory with + is generated, sometimes _
    if dirty:
        if "+" in version:
            ver, local = version.split("+")
        else:
            ver, local = version.split("_")
        assert local.endswith(dirty_tag) or local[:-1].endswith(dirty_tag[:-1])
        # ^  sometimes the day in the dirty tag has a 1-off error ¯\_(ツ)_/¯
        assert ver == exp_version
    else:
        if "+" in version:
            ver = version.split("+")
        else:
            ver = version.split("_")
        if len(ver) > 1:
            assert not ver[1].endswith(dirty_tag)
        assert ver[0] == exp_version


def test_sdist_install(demoapp):
    (demoapp.build("sdist").install())
    out = demoapp.cli("--version")
    exp = "0.0.post1.dev2"
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
    exp = "0.1.post1.dev1"
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
    demoapp.tag("v1.0", "final release").make_dirty_tree().build("sdist").install()
    out = demoapp.cli("--version")
    exp = "1.0.post1.dev0"
    check_version(out, exp, dirty=True)


# bdist works like sdist so we only try one combination
def test_bdist_install(demoapp):
    demoapp.build("bdist").install()
    out = demoapp.cli("--version")
    exp = "0.0.post1.dev2"
    check_version(out, exp, dirty=False)


def test_bdist_wheel_install(demoapp):
    demoapp.build("bdist_wheel").install()
    out = demoapp.cli("--version")
    exp = "0.0.post1.dev2"
    check_version(out, exp, dirty=False)


def test_git_repo(demoapp):
    out = demoapp.setup_py("--version")
    exp = "0.0.post1.dev2"
    check_version(out, exp, dirty=False)


def test_git_repo_dirty(demoapp):
    (
        demoapp.tag("v0.1", "first release")
        .make_dirty_tree()
        .make_commit()
        .make_dirty_tree()
    )
    out = demoapp.setup_py("--version")
    exp = "0.1.post1.dev1"
    check_version(out, exp, dirty=True)


def test_git_repo_with_1_0_tag(demoapp):
    demoapp.tag("v1.0", "final release")
    out = demoapp.setup_py("--version")
    exp = "1.0"
    check_version(out, exp, dirty=False)


def test_git_repo_with_1_0_tag_dirty(demoapp):
    demoapp.tag("v1.0", "final release").make_dirty_tree()
    out = demoapp.setup_py("--version")
    exp = "1.0.post1.dev0"
    check_version(out, exp, dirty=True)


def test_sdist_install_with_data(demoapp_data):
    demoapp_data.build("sdist").install()
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_bdist_install_with_data(demoapp_data):
    demoapp_data.build("bdist").install()
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)


def test_bdist_wheel_install_with_data(demoapp_data):
    demoapp_data.build("bdist_wheel").install()
    path = demoapp_data.installed_path()
    assert path.exists()
    assert (path / "data/__init__.py").exists()
    assert (path / "data/hello_world.txt").exists()
    assert (path / "runner.py").exists()
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
    exp = "0.0.post1.dev2"
    check_version(out, exp, dirty=False)


def test_setup_py_develop_with_data(demoapp_data):
    demoapp_data.setup_py("develop")
    out = demoapp_data.cli()
    exp = "Hello World"
    assert out.startswith(exp)
    out = demoapp_data.cli("--version")
    exp = "0.0.post1.dev2"
    check_version(out, exp, dirty=False)
