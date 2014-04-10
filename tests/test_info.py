#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import info

import git
import pytest


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


def test_is_valid_identifier():
    bad_names = ["has whitespace",
                 "has-hyphen",
                 "has_special_char$",
                 "1starts_with_digit"]
    for bad_name in bad_names:
        assert not info.is_valid_identifier(bad_name)
    valid_names = ["normal_variable_name",
                   "_private_var",
                   "_with_number1"]
    for valid_name in valid_names:
        assert info.is_valid_identifier(valid_name)


def test_make_valid_identifier():
    convertible_strings = ["has whitespaces ",
                           "has-hyphon",
                           "has special chars%"]
    for string in convertible_strings:
        assert info.make_valid_identifier(string)
    with pytest.raises(RuntimeError):
        info.make_valid_identifier("def")
