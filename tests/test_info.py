#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import info

import git


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
    assert "." in email.split("@")[1]