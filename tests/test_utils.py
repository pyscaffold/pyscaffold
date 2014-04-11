#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

from pyscaffold import utils


def test_chdir():
    curr_dir = os.getcwd()
    try:
        temp_dir = tempfile.mkdtemp()
        with utils.chdir(temp_dir):
            new_dir = os.getcwd()
        assert new_dir == temp_dir
        assert curr_dir == os.getcwd()
    finally:
        os.rmdir(temp_dir)


def test_is_valid_identifier():
    bad_names = ["has whitespace",
                 "has-hyphen",
                 "has_special_char$",
                 "1starts_with_digit"]
    for bad_name in bad_names:
        assert not utils.is_valid_identifier(bad_name)
    valid_names = ["normal_variable_name",
                   "_private_var",
                   "_with_number1"]
    for valid_name in valid_names:
        assert utils.is_valid_identifier(valid_name)


def test_make_valid_identifier():
    convertible_strings = ["has whitespaces ",
                           "has-hyphon",
                           "has special chars%"]
    for string in convertible_strings:
        assert utils.make_valid_identifier(string)
    with pytest.raises(RuntimeError):
        utils.make_valid_identifier("def")
