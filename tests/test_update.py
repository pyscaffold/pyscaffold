# -*- coding: utf-8 -*-
import logging
import os
import re
from os.path import join as path_join
from pathlib import Path

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
        self.venv.install_package("install coverage", installer="pip")
        self.running_version = parse_version(__version__)

    def install_this_pyscaffold(self):
        # Normally the following command should do the trick
        # self.venv.install_package('PyScaffold')
        # but sadly pytest-virtualenv chokes on the src-layout of PyScaffold
        # ToDo: The following will fail on Windows...
        if "TOXINIDIR" in os.environ:
            # so py.test runs within tox
            src_dir = os.environ["TOXINIDIR"]
        else:
            installed = [p for p in working_set if p.project_name == "PyScaffold"]
            msg = "Install PyScaffold with python setup.py develop!"
            assert installed, msg
            src_dir = path_join(installed[0].location, "..")

        cmd = "{python} setup.py -q develop".format(python=self.venv.python)
        self.run(cmd, cwd=src_dir)
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
        # we need the extra "" to protect from interpretation by the shell
        self.venv.install_package('install "{}"'.format(ver), installer="pip")
        installed_version = self.pyscaffold_version()._version.release[:2]
        assert installed_version == (major, minor)
        self.installed = True
        return self

    def uninstall_pyscaffold(self):
        self.run("pip uninstall -y pyscaffold")
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
