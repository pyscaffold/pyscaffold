#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import tempfile

import six

import pytest

from pyscaffold import templates, utils
from pyscaffold.exceptions import InvalidIdentifier

from .log_helpers import clear_log, last_log


def test_chdir(caplog):
    caplog.set_level(logging.INFO)
    curr_dir = os.getcwd()
    try:
        temp_dir = tempfile.mkdtemp()
        with utils.chdir(temp_dir, log=True):
            new_dir = os.getcwd()
        assert new_dir == os.path.realpath(temp_dir)
        assert curr_dir == os.getcwd()
        assert "chdir" in last_log(caplog)
    finally:
        os.rmdir(temp_dir)


def test_pretend_chdir(caplog):
    caplog.set_level(logging.INFO)
    curr_dir = os.getcwd()
    try:
        temp_dir = tempfile.mkdtemp()
        with utils.chdir(temp_dir, pretend=True):
            new_dir = os.getcwd()
        assert new_dir == curr_dir  # the directory is not changed
        assert curr_dir == os.getcwd()
        assert "chdir" in last_log(caplog)
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
    with pytest.raises(InvalidIdentifier):
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


def test_prepare_namespace():
    namespaces = utils.prepare_namespace("com")
    assert namespaces == ["com"]
    namespaces = utils.prepare_namespace("com.blue_yonder")
    assert namespaces == ["com", "com.blue_yonder"]
    with pytest.raises(InvalidIdentifier):
        utils.prepare_namespace("com.blue-yonder")


def test_best_fit_license():
    txt = "new_bsd"
    assert utils.best_fit_license(txt) == "new-bsd"
    for license in templates.licenses.keys():
        assert utils.best_fit_license(license) == license


def test_create_file(tmpfolder):
    utils.create_file('a-file.txt', 'content')
    assert tmpfolder.join('a-file.txt').read() == 'content'


def test_pretend_create_file(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    # When a file is created with pretend=True,
    utils.create_file('a-file.txt', 'content', pretend=True)
    # Then it should not be written to the disk,
    assert tmpfolder.join('a-file.txt').check() is False
    # But the operation should be logged
    for text in ('create', 'a-file.txt'):
        assert text in last_log(caplog)


def test_create_directory(tmpfolder):
    utils.create_directory('a-dir', 'content')
    assert tmpfolder.join('a-dir').check(dir=1)


def test_pretend_create_directory(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    # When a directory is created with pretend=True,
    utils.create_directory('a-dir', pretend=True)
    # Then it should not appear in the disk,
    assert tmpfolder.join('a-dir').check() is False
    # But the operation should be logged
    for text in ('create', 'a-dir'):
        assert text in last_log(caplog)


def test_update_directory(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    # When a directory exists,
    tmpfolder.join('a-dir').ensure_dir()
    # And it is created again,
    with pytest.raises(OSError):
        # Then an error should be raised,
        utils.create_directory('a-dir')

    clear_log(caplog)

    # But when it is created again with the update flag,
    utils.create_directory('a-dir', update=True)
    # Then no exception should be raised,
    # But no log should be produced also.
    assert len(caplog.records) == 0


def test_move(tmpfolder):
    # Given a file or directory exists,
    tmpfolder.join('a-file.txt').write('text')
    tmpfolder.join('a-folder').ensure_dir()
    tmpfolder.join('a-folder/another-file.txt').write('text')
    # When it is moved,
    tmpfolder.join('a-dir').ensure_dir()
    utils.move('a-file.txt', target='a-dir')
    utils.move('a-folder', target='a-dir')
    # Then the original path should not exist
    assert not tmpfolder.join('a-file.txt').check()
    assert not tmpfolder.join('a-folder').check()
    # And the new path should exist
    assert tmpfolder.join('a-dir/a-file.txt').check()
    assert tmpfolder.join('a-dir/a-folder/another-file.txt').check()


def test_move_multiple_args(tmpfolder):
    # Given several files exist,
    tmpfolder.join('a-file.txt').write('text')
    tmpfolder.join('another-file.txt').write('text')
    assert not tmpfolder.join('a-dir/a-file.txt').check()
    assert not tmpfolder.join('a-dir/another-file.txt').check()
    # When they are moved together,
    tmpfolder.join('a-dir').ensure_dir()
    utils.move('a-file.txt', 'another-file.txt', target='a-dir')
    # Then the original paths should not exist
    assert not tmpfolder.join('a-file.txt').check()
    assert not tmpfolder.join('another-file.txt').check()
    # And the new paths should exist
    assert tmpfolder.join('a-dir/a-file.txt').read() == 'text'
    assert tmpfolder.join('a-dir/another-file.txt').read() == 'text'


def test_move_non_dir_target(tmpfolder):
    # Given a file exists,
    tmpfolder.join('a-file.txt').write('text')
    assert not tmpfolder.join('another-file.txt').check()
    # When it is moved,
    utils.move('a-file.txt', target='another-file.txt')
    # Then the original path should not exist
    assert not tmpfolder.join('a-file.txt').check()
    # And the new path should exist
    assert tmpfolder.join('another-file.txt').read() == 'text'

    # Given a dir exists,
    tmpfolder.join('a-dir').ensure_dir()
    tmpfolder.join('a-dir/a-file.txt').write('text')
    assert not tmpfolder.join('another-dir/a-file.txt').check()
    # When it is moved to a path that do not exist yet,
    utils.move('a-dir', target='another-dir')
    # Then the dir should be renamed.
    assert not tmpfolder.join('a-dir').check()
    assert tmpfolder.join('another-dir/a-file.txt').read() == 'text'


def test_move_log(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    # Given a file or directory exists,
    tmpfolder.join('a-file.txt').write('text')
    tmpfolder.join('another-file.txt').write('text')
    # When it is moved without log kwarg,
    tmpfolder.join('a-dir').ensure_dir()
    utils.move('a-file.txt', target='a-dir')
    # Then no log should be created.
    assert len(caplog.records) == 0
    # When it is moved with log kwarg,
    utils.move('another-file.txt', target='a-dir', log=True)
    # Then log should be created.
    for text in ('move', 'another-file.txt', 'to', 'a-dir'):
        assert text in last_log(caplog)


def test_pretend_move(tmpfolder):
    # Given a file or directory exists,
    tmpfolder.join('a-file.txt').write('text')
    tmpfolder.join('another-file.txt').write('text')
    # When it is moved without pretend kwarg,
    tmpfolder.join('a-dir').ensure_dir()
    utils.move('a-file.txt', target='a-dir')
    # Then the src should be moved
    assert tmpfolder.join('a-dir/a-file.txt').check()
    # When it is moved with pretend kwarg,
    utils.move('another-file.txt', target='a-dir', pretend=True)
    # Then the src should not be moved
    assert not tmpfolder.join('a-dir/another-file.txt').check()
    assert tmpfolder.join('another-file.txt').check()
