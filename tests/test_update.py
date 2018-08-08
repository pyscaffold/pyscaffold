#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
from os.path import join as path_join

from pkg_resources import parse_version, working_set

import pytest

from pyscaffold import __version__, structure, update
from pyscaffold.utils import chdir

from .helpers import uniqstr


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
    def __init__(self, tmpdir, venv, pytestconfig):
        self.tmpdir = str(tmpdir)  # convert Path to str
        self.installed = False
        self.venv = venv
        self.venv_path = str(venv.virtualenv)
        self.pytestconfig = pytestconfig
        self.venv.install_package("install coverage", installer='pip')

    def install_this_pyscaffold(self):
        # Normally the following command should do the trick
        # self.venv.install_package('PyScaffold')
        # but sadly pytest-virtualenv chokes on the src-layout of PyScaffold
        installed = [p for p in working_set if p.project_name == 'PyScaffold']
        assert installed, 'Install PyScaffold with python setup.py develop!'
        # ToDo: The following will fail on Windows...
        src_dir = path_join(installed[0].location, '..')
        cmd = "cd {src_dir}; {python} setup.py -q develop".format(
            src_dir=src_dir, python=self.venv.python
        )
        self.run(cmd)
        assert __version__ == str(self.pyscaffold_version())
        self.installed = True
        return self

    def install_pyscaffold(self, major, minor):
        ver = "pyscaffold>={major}.{minor}<{major}.{next_minor}".format(
            major=major, minor=minor, next_minor=minor + 1)
        self.venv.install_package("install '{}'".format(ver),
                                  installer='pip')
        installed_version = self.pyscaffold_version()._version.release[:2]
        assert installed_version == (major, minor)
        self.installed = True
        return self

    def uninstall_pyscaffold(self):
        self.run('pip uninstall -y pyscaffold')
        assert 'PyScaffold' not in self.venv.installed_packages().keys()
        self.installed = False
        return self

    def pyscaffold_version(self):
        version = self.venv.installed_packages().get('PyScaffold', None)
        if version:
            return parse_version(version.version)
        else:
            return None

    def putup(self, *args, with_coverage=False, **kwargs):
        if with_coverage:
            # need to pass here as list since its args to coverage.py
            args = [subarg for arg in args for subarg in arg.split()]
            cmd = ['-m', 'pyscaffold.cli'] + args
        else:
            # need to pass here as string since it's the cmd itself
            cmd = ' '.join(['putup'] + list(args))
        self.run(cmd, with_coverage=with_coverage, **kwargs)
        return self

    def run(self, cmd, with_coverage=False, **kwargs):
        # pytest-virtualenv doesn't play nicely with external os.chdir
        # so let's be explicit about it...
        kwargs['cd'] = self.tmpdir
        kwargs['cwd'] = self.tmpdir
        with chdir(self.tmpdir):
            if with_coverage:
                kwargs['pytestconfig'] = self.pytestconfig
                return self.venv.run_with_coverage(cmd, **kwargs).strip()
            else:
                return self.venv.run(cmd, capture=True, **kwargs).strip()

    def get_file(self, path):
        return self.run('cat {}'.format(path))


@pytest.fixture
def venv_mgr(tmpfolder, venv, pytestconfig):
    return VenvManager(tmpfolder, venv, pytestconfig)


def test_update_version_3_0_to_3_1(venv_mgr):
    (venv_mgr.install_pyscaffold(3, 0)
             .putup('my_old_project')
             .uninstall_pyscaffold()
             .install_this_pyscaffold()
             .putup('--update my_old_project', with_coverage=True))
    # from IPython import embed; embed()
    setup_cfg = venv_mgr.get_file(path_join('my_old_project', 'setup.cfg'))
    assert '[options.entry_points]' in setup_cfg
    assert 'setup_requires' in setup_cfg
