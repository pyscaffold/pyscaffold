# -*- coding: utf-8 -*-
import logging
import os
import re
from os.path import join as path_join

from pkg_resources import parse_version, working_set

import pytest

from pyscaffold import __version__, structure, update
from pyscaffold.utils import chdir

from .helpers import uniqstr
from .system import normalize_run_args

EDITABLE_PYSCAFFOLD = re.compile(r'^-e.+pyscaffold.*$', re.M | re.I)


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
    res = update.apply_update_rule_to_file(
        fname, (fname, NO_OVERWRITE), opts)
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

    struct = {"a": ("a", NO_OVERWRITE),
              "b": "b",
              "c": {"a": "a",
                    "b": ("b", NO_OVERWRITE)},
              "d": {"a": ("a", NO_OVERWRITE),
                    "b": ("b", NO_CREATE)},
              "e": ("e", NO_CREATE)}
    dir_struct = {"a": "a",
                  "c": {"b": "b"}}
    exp_struct = {"b": "b",
                  "c": {"a": "a"},
                  "d": {"a": "a"}}
    structure.create_structure(dir_struct, opts)
    res_struct, _ = update.apply_update_rules(struct, opts)
    assert res_struct == exp_struct


class VenvManager(object):
    def __init__(self, tmpdir, venv):
        self.tmpdir = str(tmpdir)  # convert Path to str
        self.installed = False
        self.venv = venv
        self.venv_path = venv.path
        self.running_version = parse_version(__version__)

    def install_this_pyscaffold(self):
        # ToDo: The following will fail on Windows...
        if 'TOXINIDIR' in os.environ:
            # so py.test runs within tox
            src_dir = os.environ['TOXINIDIR']
        else:
            installed = [p for p in working_set
                         if p.project_name == 'PyScaffold']
            msg = 'Install PyScaffold with python setup.py develop!'
            assert installed, msg
            src_dir = path_join(installed[0].location, '..')

        cmd = "setup.py -q develop"
        self.venv.python(cmd, cwd=src_dir)
        # Make sure pyscaffold was not installed using PyPI
        assert self.running_version.public <= self.pyscaffold_version().public
        pkg_list = self.venv.pip('freeze')
        assert EDITABLE_PYSCAFFOLD.findall(pkg_list)  # METATEST
        self.installed = True
        return self

    def install_pyscaffold(self, major, minor):
        ver = "pyscaffold>={major}.{minor},<{major}.{next_minor}a0".format(
            major=major, minor=minor, next_minor=minor + 1)
        self.venv.pip('install', ver)
        installed_version = self.pyscaffold_version()._version.release[:2]
        assert installed_version == (major, minor)
        self.installed = True
        return self

    def uninstall_pyscaffold(self):
        self.run('pip uninstall -y pyscaffold')
        assert 'PyScaffold' not in self.venv.installed_packages()
        self.installed = False
        return self

    def pyscaffold_version(self):
        version = self.venv.installed_packages().get('PyScaffold', None)
        if version:
            return parse_version(version.version)
        else:
            return None

    def putup(self, *args, **kwargs):
        args = normalize_run_args(args)
        args.insert(0, 'putup')
        self.run(*args, **kwargs)
        return self

    def run(self, *args, **kwargs):
        with chdir(self.tmpdir):
            return self.venv.run(*args, **kwargs).strip()

    def coverage_run(self, *args, **kwargs):
        with chdir(self.tmpdir):
            return self.venv.coverage_run(*args, **kwargs).strip()

    def get_file(self, path):
        return self.run('cat', path)


@pytest.fixture
def venv_mgr(tmpdir, venv):
    return VenvManager(tmpdir, venv)


@pytest.mark.slow
def test_update_version_3_0_to_3_1(venv_mgr):
    project = venv_mgr.venv_path / 'my_old_project'
    (venv_mgr.install_pyscaffold(3, 0)
             .putup(project)
             .uninstall_pyscaffold()
             .install_this_pyscaffold()
             .coverage_run('-m', 'pyscaffold.cli', '--update', project))
    setup_cfg = venv_mgr.get_file(project / 'setup.cfg')
    assert '[options.entry_points]' in setup_cfg
    assert 'setup_requires' in setup_cfg


@pytest.mark.slow
def test_update_version_3_0_to_3_1_pretend(venv_mgr):
    project = venv_mgr.venv_path / 'my_old_project'
    (venv_mgr.install_pyscaffold(3, 0)
             .putup(project)
             .uninstall_pyscaffold()
             .install_this_pyscaffold()
             .coverage_run('-m', 'pyscaffold.cli',
                           '--pretend', '--update', project))
    setup_cfg = venv_mgr.get_file(project / 'setup.cfg')
    assert '[options.entry_points]' not in setup_cfg
    assert 'setup_requires' not in setup_cfg
