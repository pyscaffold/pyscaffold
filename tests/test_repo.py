# -*- coding: utf-8 -*-
import os.path
import shutil
import subprocess
import sys

import pytest

from pyscaffold import api, cli, repo, shell, structure, update, utils


def test_init_commit_repo(tmpfolder):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
            "dummy": None,
        }
    }
    structure.create_structure(struct, {})
    dummy_file = os.path.join(project, "dummy")
    with open(dummy_file, "w"):
        os.utime(dummy_file, None)
    repo.init_commit_repo(project, struct)
    assert os.path.exists(os.path.join(project, ".git"))


def test_pretend_init_commit_repo(tmpfolder):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
            "dummy": None,
        }
    }
    structure.create_structure(struct, {})
    dummy_file = os.path.join(project, "dummy")
    with open(dummy_file, "w"):
        os.utime(dummy_file, None)
    repo.init_commit_repo(project, struct, pretend=True)
    assert not os.path.exists(os.path.join(project, ".git"))


def test_init_commit_repo_with_wrong_structure(tmpfolder):
    project = "my_project"
    struct = {project: {"my_file": type("StrangeType", (object,), {})}}
    os.mkdir(project)
    with pytest.raises(RuntimeError):
        repo.init_commit_repo(project, struct)


def test_add_tag(tmpfolder):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
        }
    }
    structure.create_structure(struct, {})
    repo.init_commit_repo(project, struct)
    repo.add_tag(project, "v0.0")
    repo.add_tag(project, "v0.1", "Message with whitespace")


@pytest.mark.slow
def test_version_of_subdir(tmpfolder):
    projects = ["main_project", "inner_project"]
    for project in projects:
        opts = cli.parse_args([project])
        opts = cli.process_opts(opts)
        _, opts = api.get_default_options({}, opts)
        struct, _ = structure.define_structure({}, opts)
        struct, _ = update.apply_update_rules(struct, opts)
        structure.create_structure(struct, {})
        repo.init_commit_repo(project, struct)
    utils.rm_rf(os.path.join("inner_project", ".git"))
    shutil.move("inner_project", "main_project/inner_project")
    with utils.chdir("main_project"):
        main_version = (
            subprocess.check_output([sys.executable, "setup.py", "--version"])
            .strip()
            .splitlines()[-1]
        )
        with utils.chdir("inner_project"):
            inner_version = (
                subprocess.check_output([sys.executable, "setup.py", "--version"])
                .strip()
                .splitlines()[-1]
            )
    assert main_version.strip() == inner_version.strip()


def test_is_git_repo(tmpfolder):
    assert not repo.is_git_repo("/a-folder/that-not/exist")
    newdir = tmpfolder.join("new").ensure_dir()
    assert not repo.is_git_repo(str(newdir))
    newdir.chdir()
    shell.git("init")
    tmpfolder.chdir()
    assert repo.is_git_repo(str(newdir))


def test_get_git_root(tmpfolder):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
        }
    }
    structure.create_structure(struct, {})
    repo.init_commit_repo(project, struct)
    with utils.chdir(project):
        git_root = repo.get_git_root()
    assert os.path.basename(git_root) == project


def test_get_git_root_with_nogit(tmpfolder, nogit_mock):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
        }
    }
    structure.create_structure(struct, {})
    with utils.chdir(project):
        git_root = repo.get_git_root(default=".")
    assert git_root == "."


def test_get_git_root_with_nonegit(tmpfolder, nonegit_mock):
    project = "my_project"
    struct = {
        project: {
            "my_file": "Some other content",
            "my_dir": {"my_file": "Some more content"},
        }
    }
    structure.create_structure(struct, {})
    with utils.chdir(project):
        git_root = repo.get_git_root(default=".")
    assert git_root == "."
