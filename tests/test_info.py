#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import getpass

import pytest

from pyscaffold import info
from .fixtures import git_mock, nogit_mock

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


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
    assert info.git_is_installed()


def test_git_is_not_installed(nogit_mock):
    assert not info.git_is_installed()
