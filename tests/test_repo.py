#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import shutil
import subprocess

import pytest
from pyscaffold import repo, structure, cli, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_init_commit_repo(tmpdir):  # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"},
        "dummy": None}
    }
    structure.create_structure(struct)
    dummy_file = os.path.join(project, "dummy")
    with open(dummy_file, 'w'):
        os.utime(dummy_file, None)
    repo.init_commit_repo(project, struct)
    assert os.path.exists(os.path.join(project, ".git"))


def test_init_commit_repo_with_wrong_structure(tmpdir):  # noqa
    project = "my_project"
    struct = {project: {
        "my_file": type("StrangeType", (object,), {})}}
    os.mkdir(project)
    with pytest.raises(RuntimeError):
        repo.init_commit_repo(project, struct)


def test_add_tag(tmpdir):  # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"}}
    }
    structure.create_structure(struct)
    repo.init_commit_repo(project, struct)
    repo.add_tag(project, "v0.0")
    repo.add_tag(project, "v0.1", "Message with whitespace")


def test_version_of_subdir(tmpdir): # noqa
    projects = ["main_project", "inner_project"]
    for project in projects:
        opts = cli.parse_args([project])
        opts = cli.get_default_opts(opts['project'], **opts)
        struct = structure.make_structure(opts)
        structure.create_structure(struct)
        repo.init_commit_repo(project, struct)
    shutil.rmtree(os.path.join('inner_project', '.git'))
    shutil.move('inner_project', 'main_project/inner_project')
    with utils.chdir('main_project'):
        main_version = subprocess.check_output([
            'python', 'setup.py', '--version']).strip()
        with utils.chdir('inner_project'):
            inner_version = subprocess.check_output([
                'python', 'setup.py', '--version']).strip()
    assert main_version == inner_version


def test_get_git_root(tmpdir): # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"}}
    }
    structure.create_structure(struct)
    repo.init_commit_repo(project, struct)
    with utils.chdir(project):
        git_root = repo.get_git_root()
    assert os.path.basename(git_root) == project


def test_get_git_root(tmpdir): # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"}}
    }
    structure.create_structure(struct)
    repo.init_commit_repo(project, struct)
    with utils.chdir(project):
        git_root = repo.get_git_root()
    assert os.path.basename(git_root) == project


def test_get_git_root_with_nogit(tmpdir, nogit_mock): # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"}}
    }
    structure.create_structure(struct)
    with utils.chdir(project):
        git_root = repo.get_git_root(default='.')
    assert git_root == '.'


def test_get_git_root_with_nonegit(tmpdir, nonegit_mock): # noqa
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"}}
    }
    structure.create_structure(struct)
    with utils.chdir(project):
        git_root = repo.get_git_root(default='.')
    assert git_root == '.'
