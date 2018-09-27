#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import os
import socket

import pytest

from pyscaffold import cli, exceptions, info, repo, structure, templates


def test_username_with_git(git_mock):
    username = info.username()
    assert isinstance(username, str)
    assert len(username) > 0


def test_username_with_no_git(nogit_mock):
    username = info.username()
    assert isinstance(username, str)
    assert getpass.getuser() == username


def test_email_with_git(git_mock):
    email = info.email()
    assert "@" in email


def test_email_with_nogit(nogit_mock):
    email = info.email()
    assert socket.gethostname() == email.split("@")[1]


def test_git_is_installed(git_mock):
    assert info.is_git_installed()


def test_git_is_wrongely_installed(nogit_mock):
    assert not info.is_git_installed()


def test_git_is_not_installed(nonegit_mock):
    assert not info.is_git_installed()


def test_is_git_configured(git_mock):
    assert info.is_git_configured()


def test_is_git_not_configured(noconfgit_mock):
    assert not info.is_git_configured()


def test_check_git_not_installed(nonegit_mock):
    with pytest.raises(exceptions.GitNotInstalled):
        info.check_git()


def test_check_git_not_configured(noconfgit_mock):
    with pytest.raises(exceptions.GitNotConfigured):
        info.check_git()


def test_check_git_installed_and_configured(git_mock):
    info.check_git()


def test_project_without_args(tmpfolder):
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    cli.main(old_args)
    args = ["my_project"]
    opts = cli.parse_args(args)
    opts = cli.process_opts(opts)
    new_opts = info.project(opts)
    assert new_opts['url'] == "http://www.blue-yonder.com/"
    assert new_opts['package'] == "my_project"
    assert new_opts['license'] == "mit"
    assert new_opts['description'] == "my description"


def test_project_with_args(tmpfolder):
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    cli.main(old_args)
    args = ["my_project", "-u", "http://www.google.com/",
            "-d", "other description"]
    opts = cli.parse_args(args)
    opts = cli.process_opts(opts)
    new_opts = info.project(opts)
    assert new_opts['url'] == "http://www.google.com/"
    assert new_opts['package'] == "my_project"
    assert new_opts['description'] == "other description"


def test_project_with_no_setup(tmpfolder):
    os.mkdir("my_project")
    args = ["my_project"]
    opts = cli.parse_args(args)
    opts = cli.process_opts(opts)
    with pytest.raises(FileNotFoundError):
        info.project(opts)


def test_project_with_wrong_setup(tmpfolder):
    os.mkdir("my_project")
    open("my_project/setup.py", 'a').close()
    args = ["my_project"]
    opts = cli.parse_args(args)
    opts = cli.process_opts(opts)
    with pytest.raises(FileNotFoundError):
        info.project(opts)


def test_best_fit_license():
    txt = "new_bsd"
    assert info.best_fit_license(txt) == "new-bsd"
    for license in templates.licenses.keys():
        assert info.best_fit_license(license) == license


def test_dirty_workspace(tmpfolder):
    project = "my_project"
    struct = {project: {"dummyfile": "NO CONTENT"}}
    structure.create_structure(struct, {})
    repo.init_commit_repo(project, struct)
    path = tmpfolder / project
    assert info.is_git_workspace_clean(path)
    with open(str(path / "dummyfile"), 'w') as fh:
        fh.write('CHANGED\n')
    assert not info.is_git_workspace_clean(path)
