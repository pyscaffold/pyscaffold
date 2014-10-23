#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import six
import pytest

from pyscaffold import utils
from pyscaffold import runner


def test_chdir():
    curr_dir = os.getcwd()
    try:
        temp_dir = tempfile.mkdtemp()
        with utils.chdir(temp_dir):
            new_dir = os.getcwd()
        assert new_dir == os.path.realpath(temp_dir)
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


def test_safe_get():
    args = ["my-project", "-u", "http://www.blue-yonder.com/"]
    args = runner.parse_args(args)
    assert utils.safe_get(args, "url") == "http://www.blue-yonder.com/"
    assert utils.safe_get(args, "non_existent") is None


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
    def func(_):
        raise RuntimeError("Exception raised")
    with pytest.raises(SystemExit):
        func(1)


def test_ObjKeeper():

    @six.add_metaclass(utils.ObjKeeper)
    class MyClass(object):
        pass

    obj1 = MyClass()
    obj2 = MyClass()
    assert MyClass.instances[MyClass][0] is obj1
    assert MyClass.instances[MyClass][1] is obj2


def test_capture_objs():
    import string
    ref = utils.capture_objs(string.Template)
    my_template = string.Template("")
    assert my_template is ref[-1]


def test_git2pep440():
    ver = "1.0-1-gacf677d"
    assert utils.git2pep440(ver) == "1.0.post.dev1"
    ver = "2.0"
    assert utils.git2pep440(ver) == "2.0"
    ver = "2.0-2-g68b1b7b-dirty"
    assert utils.git2pep440(ver) == "2.0.post.dev3.pre"
    ver = "3.0-dirty"
    assert utils.git2pep440(ver) == "3.0.post.dev1.pre"
    with pytest.raises(RuntimeError):
        ver = "3.0-dirty-1-1-1"
        utils.git2pep440(ver)


def test_levenshtein():
    s1 = "born"
    s2 = "burn"
    assert utils.levenshtein(s1, s2) == 1
    s2 = "burnt"
    assert utils.levenshtein(s1, s2) == 2
    assert utils.levenshtein(s2, s1) == 2
    s2 = ""
    assert utils.levenshtein(s2, s1) == 4
