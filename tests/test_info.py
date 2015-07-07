#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import getpass
import os
import socket

import pytest
from pyscaffold import info, cli
from six import string_types

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_username_with_git(git_mock):  # noqa
    username = info.username()
    assert isinstance(username, string_types)
    assert len(username) > 0


def test_username_with_no_git(nogit_mock):  # noqa
    username = info.username()
    assert isinstance(username, string_types)
    assert getpass.getuser() == username


def test_email_with_git(git_mock):  # noqa
    email = info.email()
    assert "@" in email


def test_email_with_nogit(nogit_mock):  # noqa
    email = info.email()
    assert socket.gethostname() == email.split("@")[1]


def test_git_is_installed(git_mock):  # noqa
    assert info.is_git_installed()


def test_git_is_not_installed(nogit_mock):  # noqa
    assert not info.is_git_installed()


def test_is_git_configured(git_mock):  # noqa
    assert info.is_git_configured()


def test_is_git_not_configured(noconfgit_mock):  # noqa
    assert not info.is_git_configured()


def test_project_raises():
    opts = {"project": "non_existant"}
    with pytest.raises(RuntimeError):
        info.project(opts)


def test_project_without_args(tmpdir):  # noqa
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    cli.main(old_args)
    args = ["my_project"]
    opts = cli.parse_args(args)
    new_opts = info.project(opts)
    assert new_opts['url'] == "http://www.blue-yonder.com/"
    assert new_opts['package'] == "my_project"
    assert new_opts['license'] == "none"
    assert new_opts['description'] == "my description"


def test_project_with_args(tmpdir):  # noqa
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    cli.main(old_args)
    args = ["my_project", "-u", "http://www.google.com/",
            "-d", "other description"]
    opts = cli.parse_args(args)
    new_opts = info.project(opts)
    assert new_opts['url'] == "http://www.blue-yonder.com/"
    assert new_opts['package'] == "my_project"
    assert new_opts['description'] == "my description"


def test_project_with_no_setup(tmpdir):  # noqa
    os.mkdir("my_project")
    args = ["my_project"]
    args = cli.parse_args(args)
    with pytest.raises(RuntimeError):
        info.project(args)


def test_project_with_wrong_setup(tmpdir):  # noqa
    os.mkdir("my_project")
    open("my_project/setup.py", 'a').close()
    args = ["my_project"]
    args = cli.parse_args(args)
    with pytest.raises(RuntimeError):
        info.project(args)
