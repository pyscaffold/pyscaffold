#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

from pyscaffold import utils
from pyscaffold import runner


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
    assert utils.make_valid_identifier("has whitespaces ") == "has_whitespaces"
    assert utils.make_valid_identifier("has-hyphon") == "has_hyphon"
    assert utils.make_valid_identifier("special chars%") == "special_chars"
    assert utils.make_valid_identifier("UpperCase") == "uppercase"
    with pytest.raises(RuntimeError):
        utils.make_valid_identifier("def")


def test_safe_set():
    args = ["my-project", "-u", "http://www.blue-yonder.com/"]
    args = runner.parse_args(args)
    utils.safe_set(args, "new_option", "value")
    assert args.new_option == "value"
    utils.safe_set(args, "license", "my license")
    assert args.license == "my license"
    utils.safe_set(args, "url", "http://www.python.org/")
    assert args.url == "http://www.blue-yonder.com/"


def test_list2str():
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python']
    class_str = utils.list2str(classifiers, indent=len("classifiers = ") + 1)
    exp_class_str = """\
['Development Status :: 4 - Beta',
               'Programming Language :: Python']"""
    assert class_str == exp_class_str
    classifiers = ['Development Status :: 4 - Beta']
    class_str = utils.list2str(classifiers, indent=len("classifiers = ") + 1)
    assert class_str == "['Development Status :: 4 - Beta']"
    classifiers = []
    class_str = utils.list2str(classifiers, indent=len("classifiers = ") + 1)
    assert class_str == "[]"


def test_exceptions2exit():
    @utils.exceptions2exit([RuntimeError])
    def func(a):
        raise RuntimeError("Exception raised")
    with pytest.raises(SystemExit):
        func(1)
