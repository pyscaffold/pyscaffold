#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyscaffold.api import Scaffold

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


def test_merge_structure_basics():
    # Given an existing structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "1",
                                                   "d": "2"}}})
    # when it is merged to another structure with some common folder
    extra_files = {"a": {"b": {"c": "0"},
                         "e": "2"},
                   "f": {"g": {"h": "0"}}}
    scaffold.merge_structure(extra_files)
    # then the result, should contain both files from the original and the
    # merged structure,
    assert scaffold.structure["a"]["b"]["d"] == "2"
    assert scaffold.structure["f"]["g"]["h"] == "0"
    assert scaffold.structure["a"]["e"] == "2"
    # the common leaves should be overridden and a tuple (content, rule)
    assert scaffold.structure["a"]["b"]["c"] == ("0", None)


def test_merge_structure_rules_just_in_original():
    # When an update rule exists in the original structure,
    scaffold = Scaffold({}, structure={"a": {"b": ("0", Scaffold.NO_CREATE)}})
    # but not in the merged,
    extra_files = {"a": {"b": "3"}}
    scaffold.merge_structure(extra_files)
    # then just the content should be updated
    # and the rule should be kept identical
    assert scaffold.structure["a"]["b"] == ("3", Scaffold.NO_CREATE)


def test_merge_structure_rules_just_in_merged():
    # When an update rule does not exist in the original structure,
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # but exists in the merged,
    extra_files = {"a": {"b": (None, Scaffold.NO_CREATE)}}
    scaffold.merge_structure(extra_files)
    # then just the rule should be updated
    # and the content should be kept identical
    assert scaffold.structure["a"]["b"] == ("0", Scaffold.NO_CREATE)


def test_empty_string_ensure_empty_file_during_merge():
    # When the original structure contains a leaf,
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # and the merged structure overrides it with an empty content
    extra_files = {"a": {"b": ""}}
    scaffold.merge_structure(extra_files)
    # then the resulting content should exist and be empty
    assert scaffold.structure["a"]["b"][0] == ""


def test_ensure_file_nested():
    # When the original structure does not contain a leaf
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # that is added using the ensure_file method,
    scaffold.ensure_file("f", content="1", path=["a", "c", "d", "e"])
    # then all the necessary parent folder should be included
    assert isinstance(scaffold.structure["a"]["c"], dict)
    assert isinstance(scaffold.structure["a"]["c"]["d"], dict)
    assert isinstance(scaffold.structure["a"]["c"]["d"]["e"], dict)
    # and the file itself
    assert scaffold.structure["a"]["c"]["d"]["e"]["f"][0] == "1"


def test_ensure_file_overriden():
    # When the original structure contains a leaf
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # that is overridden using the ensure_file method,
    scaffold.ensure_file("b", content="1", path=["a"])
    # and the file content should be overridden
    assert scaffold.structure["a"]["b"][0] == "1"


def test_ensure_file_path():
    # When the ensure_path method is called with an string path
    scaffold = Scaffold({})
    scaffold.ensure_file("d", content="1", path="a/b/c")
    # Then the effect should be the same as if it were split
    assert scaffold.structure["a"]["b"]["c"]["d"][0] == "1"
