#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyscaffold.api import Helper as helpers


def test_merge_basics():
    # Given an existing structure,
    structure = {"a": {"b": {"c": "1",
                             "d": "2"}}}
    # when it is merged to another structure with some common folder
    extra_files = {"a": {"b": {"c": "0"},
                         "e": "2"},
                   "f": {"g": {"h": "0"}}}
    structure = helpers.merge(structure, extra_files)
    # then the result, should contain both files from the original and the
    # merged structure,
    assert structure["a"]["b"]["d"] == "2"
    assert structure["f"]["g"]["h"] == "0"
    assert structure["a"]["e"] == "2"
    # the common leaves should be overridden and a tuple (content, rule)
    assert structure["a"]["b"]["c"] == "0"


def test_merge_rules_just_in_original():
    # When an update rule exists in the original structure,
    structure = {"a": {"b": ("0", helpers.NO_CREATE)}}
    # but not in the merged,
    extra_files = {"a": {"b": "3"}}
    structure = helpers.merge(structure, extra_files)
    # then just the content should be updated
    # and the rule should be kept identical
    assert structure["a"]["b"] == ("3", helpers.NO_CREATE)


def test_merge_rules_just_in_merged():
    # When an update rule does not exist in the original structure,
    structure = {"a": {"b": "0"}}
    # but exists in the merged,
    extra_files = {"a": {"b": (None, helpers.NO_CREATE)}}
    structure = helpers.merge(structure, extra_files)
    # then just the rule should be updated
    # and the content should be kept identical
    assert structure["a"]["b"] == ("0", helpers.NO_CREATE)


def test_empty_string_leads_to_empty_file_during_merge():
    # When the original structure contains a leaf,
    structure = {"a": {"b": "0"}}
    # and the merged structure overrides it with an empty content
    extra_files = {"a": {"b": ""}}
    structure = helpers.merge(structure, extra_files)
    # then the resulting content should exist and be empty
    assert structure["a"]["b"] == ""


def test_ensure_nested():
    # When the original structure does not contain a leaf
    structure = {"a": {"b": "0"}}
    # that is added using the ensure method,
    structure = helpers.ensure(structure, "f", content="1",
                               path=["a", "c", "d", "e"])
    # then all the necessary parent folder should be included
    assert isinstance(structure["a"]["c"], dict)
    assert isinstance(structure["a"]["c"]["d"], dict)
    assert isinstance(structure["a"]["c"]["d"]["e"], dict)
    # and the file itself
    assert structure["a"]["c"]["d"]["e"]["f"] == "1"


def test_ensure_overriden():
    # When the original structure contains a leaf
    structure = {"a": {"b": "0"}}
    # that is overridden using the ensure method,
    structure = helpers.ensure(structure, "b", content="1", path=["a"])
    # and the file content should be overridden
    assert structure["a"]["b"] == "1"


def test_ensure_path():
    # When the ensure method is called with an string path
    structure = {}
    structure = helpers.ensure(structure, "d", content="1", path="a/b/c")
    # Then the effect should be the same as if it were split
    assert structure["a"]["b"]["c"]["d"] == "1"


def test_reject():
    # When the original structure contain a leaf
    structure = {"a": {"b": {"c": "0"}}}
    # that is removed using the reject method,
    structure = helpers.reject(structure, "c", path=["a", "b"])
    # then the structure should not contain the file
    assert "c" not in structure["a"]["b"]


def test_reject_without_ancestor():
    # Given a defined structure,
    structure = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the structure,
    structure = helpers.reject(structure, "c", path="a/b/x")
    # then the structure should be the same
    assert structure["a"]["b"]["c"] == "0"
    assert len(structure["a"]["b"]["c"]) == 1
    assert len(structure["a"]["b"]) == 1
    assert len(structure["a"]) == 1


def test_reject_without_file():
    # Given a defined structure,
    structure = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the structure,
    structure = helpers.reject(structure, "x", path="a/b")
    # then the structure should be the same
    assert structure["a"]["b"]["c"] == "0"
    assert len(structure["a"]["b"]["c"]) == 1
    assert len(structure["a"]["b"]) == 1
    assert len(structure["a"]) == 1
