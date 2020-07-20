# -*- coding: utf-8 -*-
import logging
import os
import re
from configparser import ConfigParser
from os.path import join as path_join
from pathlib import Path
from textwrap import dedent

from pkg_resources import parse_version, working_set

import pytest

from pyscaffold import __version__, structure, update
from pyscaffold.utils import chdir

from .helpers import uniqstr

EDITABLE_PYSCAFFOLD = re.compile(r"^-e.+pyscaffold.*$", re.M | re.I)


def test_apply_update_rules_to_file(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE

    # When update is False (no project exists yet) always update
    opts = {"update": False}
    res = update.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When content is string always update
    opts = {"update": True}
    res = update.apply_update_rule_to_file("a", "a", opts)
    assert res == "a"
    # When force is True always update
    opts = {"update": True, "force": True}
    res = update.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When file exist, update is True, rule is NO_OVERWRITE, do nothing
    opts = {"update": True}
    fname = uniqstr()
    tmpfolder.join(fname).write("content")
    res = update.apply_update_rule_to_file(fname, (fname, NO_OVERWRITE), opts)
    assert res is None
    logs = caplog.text
    assert re.search("skip.*" + fname, logs)
    # When file does not exist, update is True, but rule is NO_CREATE, do
    # nothing
    opts = {"update": True}
    fname = uniqstr()
    res = update.apply_update_rule_to_file(fname, (fname, NO_CREATE), opts)
    assert res is None
    assert re.search("skip.*" + fname, caplog.text)


def test_apply_update_rules(tmpfolder):
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE
    opts = dict(update=True)

    struct = {
        "a": ("a", NO_OVERWRITE),
        "b": "b",
        "c": {"a": "a", "b": ("b", NO_OVERWRITE)},
        "d": {"a": ("a", NO_OVERWRITE), "b": ("b", NO_CREATE)},
        "e": ("e", NO_CREATE),
    }
    dir_struct = {"a": "a", "c": {"b": "b"}}
    exp_struct = {"b": "b", "c": {"a": "a"}, "d": {"a": "a"}}
    structure.create_structure(dir_struct, opts)
    res_struct, _ = update.apply_update_rules(struct, opts)
    assert res_struct == exp_struct


class VenvManager(object):
    def __init__(self, tmpdir, venv, pytestconfig):
        self.tmpdir = str(tmpdir)  # convert Path to str
        self.installed = False
        self.venv = venv
        self.venv_path = str(venv.virtualenv)
        self.pytestconfig = pytestconfig
        self.install("coverage")
        self.running_version = parse_version(__version__)

    def install(self, pkg=None, editable=False):
        pkg = f'"{pkg}"'  # Windows requires double quotes to work properly with ranges
        if editable:
            pkg = f"--editable {pkg}"

        python = self.venv.python
        assert Path(python).exists()

        # Sometimes Windows complain about SSL, despite all the efforts on using a env
        # var for trusted hosts
        return self.run(
            f"{python} -m pip install {pkg} --trusted-host pypi.python.org "
            "--trusted-host files.pythonhosted.org --trusted-host pypi.org"
        )

    def install_this_pyscaffold(self):
        # Normally the following command should do the trick
        # self.venv.install_package('PyScaffold')
        # but sadly pytest-virtualenv chokes on the src-layout of PyScaffold
        if "TOXINIDIR" in os.environ:
            # so py.test runs within tox
            src_dir = Path(os.environ["TOXINIDIR"])
            logging.debug("SRC via TOXINIDIR: %s", src_dir)
        else:
            installed = [p for p in iter(working_set) if p.project_name == "PyScaffold"]
            msg = "Install PyScaffold with python setup.py develop!"
            assert installed, msg
            location = Path(installed[0].location)
            src_dir = location.parent
            logging.debug("SRC via working_set: %s, location: %s", src_dir, location)

        assert src_dir.exists(), f"{src_dir} is supposed to exist"
        self.install(src_dir, editable=True)
        # Make sure pyscaffold was not installed using PyPI
        assert self.running_version.public <= self.pyscaffold_version().public
        pkg_list = self.run("{} -m pip freeze".format(self.venv.python))
        assert EDITABLE_PYSCAFFOLD.findall(pkg_list)
        self.installed = True
        return self

    def install_pyscaffold(self, major, minor):
        ver = "pyscaffold>={major}.{minor},<{major}.{next_minor}a0".format(
            major=major, minor=minor, next_minor=minor + 1
        )
        self.install(ver)
        installed_version = self.pyscaffold_version()._version.release[:2]
        assert installed_version == (major, minor)
        self.installed = True
        return self

    def uninstall_pyscaffold(self):
        self.run("{} -m pip uninstall -y pyscaffold".format(self.venv.python))
        assert "PyScaffold" not in self.venv.installed_packages().keys()
        self.installed = False
        return self

    def pyscaffold_version(self):
        version = self.venv.installed_packages().get("PyScaffold", None)
        if version:
            return parse_version(version.version)
        else:
            return None

    def putup(self, *args, with_coverage=False, **kwargs):
        if with_coverage:
            # need to pass here as list since its args to coverage.py
            args = [subarg for arg in args for subarg in arg.split()]
            putup_path = path_join(self.venv_path, "bin", "putup")
            cmd = [putup_path] + args
        else:
            # need to pass here as string since it's the cmd itself
            cmd = " ".join(["putup"] + list(args))
        self.run(cmd, with_coverage=with_coverage, **kwargs)
        return self

    def run(self, cmd, with_coverage=False, **kwargs):
        if with_coverage:
            kwargs.setdefault("pytestconfig", self.pytestconfig)
            # change to directory where .coverage needs to be created
            kwargs.setdefault("cd", os.getcwd())
            return self.venv.run_with_coverage(cmd, **kwargs).strip()
        else:
            with chdir(self.tmpdir):
                kwargs.setdefault("cwd", self.tmpdir)
                return self.venv.run(cmd, capture=True, **kwargs).strip()

    def get_file(self, path):
        with chdir(self.tmpdir):
            return Path(path).read_text()


@pytest.fixture
def venv_mgr(tmpdir, venv, pytestconfig):
    return VenvManager(tmpdir, venv, pytestconfig)


@pytest.mark.slow
def test_update_version_3_0_to_3_1(with_coverage, venv_mgr):
    project = path_join(venv_mgr.venv_path, "my_old_project")
    (
        venv_mgr.install_pyscaffold(3, 0)
        .putup(project)
        .uninstall_pyscaffold()
        .install_this_pyscaffold()
        .putup("--update {}".format(project), with_coverage=with_coverage)
    )
    setup_cfg = venv_mgr.get_file(path_join(project, "setup.cfg"))
    assert "[options.entry_points]" in setup_cfg
    assert "setup_requires" in setup_cfg


@pytest.mark.slow
def test_update_version_3_0_to_3_1_pretend(with_coverage, venv_mgr):
    project = path_join(venv_mgr.venv_path, "my_old_project")
    (
        venv_mgr.install_pyscaffold(3, 0)
        .putup(project)
        .uninstall_pyscaffold()
        .install_this_pyscaffold()
        .putup("--pretend --update {}".format(project), with_coverage=with_coverage)
    )
    setup_cfg = venv_mgr.get_file(path_join(project, "setup.cfg"))
    assert "[options.entry_points]" not in setup_cfg
    assert "setup_requires" not in setup_cfg


@pytest.mark.slow
def test_inplace_update(with_coverage, venv_mgr):
    # Given an existing project
    project = Path(venv_mgr.tmpdir) / "my-ns-proj"
    (
        venv_mgr.install_this_pyscaffold().putup(
            "--package project --namespace my_ns {}".format(project)
        )
    )

    # With an existing configuration
    parser = ConfigParser()
    parser.read(project / "setup.cfg")
    assert parser["metadata"]["name"] == "my-ns-proj"
    assert parser["pyscaffold"]["package"] == "project"
    assert parser["pyscaffold"]["namespace"] == "my_ns"

    # And without some extensions
    for file in ("tox.ini", ".pre-commit-config.yaml", ".isort.cfg"):
        assert not Path(project, file).exists()

    # When the project is updated
    # without repeating the information already given
    # but adding some information/extensions
    with chdir(str(project)):
        (
            venv_mgr.putup(
                "-vv --description asdf --tox --pre-commit --update .",
                with_coverage=with_coverage,
                cwd=str(project),
            )
        )

    # Then existing configuration should be preserved + the additions
    parser = ConfigParser()
    parser.read(project / "setup.cfg")
    assert parser["metadata"]["name"] == "my-ns-proj"
    assert parser["pyscaffold"]["package"] == "project"
    assert parser["pyscaffold"]["namespace"] == "my_ns"

    # Some information (metadata) require manual update
    # unless the --force option is used
    assert parser["metadata"]["description"] != "asdf"

    # New extensions should take effect
    for file in ("tox.ini", ".pre-commit-config.yaml", ".isort.cfg"):
        assert Path(project, file).exists()

    # While using the existing information
    parser = ConfigParser()
    parser.read(project / ".isort.cfg")
    assert parser["settings"]["known_first_party"] == "my_ns"


@pytest.fixture
def existing_config(tmpfolder):
    config = dedent(
        """\
        [options]
        setup_requires = pyscaffold>=3.2a0,<3.3a0;other<=9.9

        [pyscaffold]
        version = 3.2.2
        """
    )
    cfg = Path(tmpfolder) / "setup.cfg"
    cfg.write_text(config)

    yield cfg


def test_update_pyscaffold_version(existing_config):
    # Given an existing setup.cfg with outdated setup_requires and pyscaffold version,
    # when we update it
    update.update_pyscaffold_version(existing_config, False)
    cfg = ConfigParser()
    cfg.read(str(existing_config))
    # Then the new setup_requirements should be included
    deps = cfg["options"]["setup_requires"]
    assert "setuptools_scm" in deps
    assert "wheel" in deps
    # Existing deps should be kept unchanged
    assert "other<=9.9" in deps
    # But pyscaffold shouldn't (not required at build time anymore)
    assert "pyscaffold" not in deps
    # Finally pyscaffold.version should be updated
    assert cfg["pyscaffold"]["version"] == __version__
