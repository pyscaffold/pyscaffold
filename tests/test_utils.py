#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest
import six
from pyscaffold import utils, templates
from pyscaffold.structure import create_structure


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
    classifiers = ['Development Status :: 4 - Beta']
    class_str = utils.list2str(classifiers, brackets=False)
    assert class_str == "'Development Status :: 4 - Beta'"
    class_str = utils.list2str(classifiers, brackets=False, quotes=False)
    assert class_str == "Development Status :: 4 - Beta"
    class_str = utils.list2str(classifiers, brackets=True, quotes=False)
    assert class_str == "[Development Status :: 4 - Beta]"


def test_exceptions2exit():
    @utils.exceptions2exit([RuntimeError])
    def func(_):
        raise RuntimeError("Exception raised")
    with pytest.raises(SystemExit):
        func(1)


def test_levenshtein():
    s1 = "born"
    s2 = "burn"
    assert utils.levenshtein(s1, s2) == 1
    s2 = "burnt"
    assert utils.levenshtein(s1, s2) == 2
    assert utils.levenshtein(s2, s1) == 2
    s2 = ""
    assert utils.levenshtein(s2, s1) == 4


def test_utf8_encode():
    s_in = six.u('äüä')
    s_out = utils.utf8_encode(s_in)
    assert isinstance(s_out, six.string_types)


def test_utf8_decode():
    s_in = "äüä"
    s_out = utils.utf8_decode(s_in)
    assert isinstance(s_out, six.string_types)


def test_get_files(tmpdir):  # noqa
    struct = {'subdir': {'script.py': '#Python script...'},
              'root_script.py': '#Root Python script...'}
    create_structure(struct)
    files = utils.get_files("*.py")
    assert 'root_script.py' in files
    assert 'subdir/script.py' not in files
    files = utils.get_files("**.py")
    assert 'root_script.py' in files
    assert 'subdir/script.py' in files


def test_prepare_namespace():
    namespaces = utils.prepare_namespace("com")
    assert namespaces == ["com"]
    namespaces = utils.prepare_namespace("com.blue_yonder")
    assert namespaces == ["com", "com.blue_yonder"]
    with pytest.raises(RuntimeError):
        utils.prepare_namespace("com.blue-yonder")


def test_best_fit_license():
    txt = "new_bsd"
    assert utils.best_fit_license(txt) == "new-bsd"
    for license in templates.licenses.keys():
        assert utils.best_fit_license(license) == license
