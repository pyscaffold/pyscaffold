#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import info

import git
import pytest

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_get_global_gitconfig():
    gitconfig = info.get_global_gitconfig()
    assert isinstance(gitconfig, git.config.GitConfigParser)


def test_username():
    username = info.username()
    assert isinstance(username, str)
    assert len(username) > 0


def test_email():
    email = info.email()
    assert "@" in email
