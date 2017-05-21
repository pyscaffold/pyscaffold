#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import exists as path_exists

from pyscaffold.api import Scaffold, create_project, get_default_opts

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
    assert scaffold.structure["a"]["b"] == ("", None)


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
    assert scaffold.structure["a"]["c"]["d"]["e"]["f"] == ("1", None)


def test_ensure_file_overriden():
    # When the original structure contains a leaf
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # that is overridden using the ensure_file method,
    scaffold.ensure_file("b", content="1", path=["a"])
    # and the file content should be overridden
    assert scaffold.structure["a"]["b"] == ("1", None)


def test_ensure_file_path():
    # When the ensure_path method is called with an string path
    scaffold = Scaffold({})
    scaffold.ensure_file("d", content="1", path="a/b/c")
    # Then the effect should be the same as if it were split
    assert scaffold.structure["a"]["b"]["c"]["d"] == ("1", None)


def test_reject_file():
    # When the original structure contain a leaf
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # that is removed using the reject_file method,
    scaffold.reject_file("c", path=["a", "b"])
    # then the structure should not contain the file
    assert "c" not in scaffold.structure["a"]["b"]


def test_reject_file_without_ancestor():
    # Given a defined structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # when someone tries to remvoe a file using the reject_file method
    # but one of its ancestor does not exist in the structure,
    scaffold.reject_file("c", path="a/b/x")
    # then the structure should be the same
    assert scaffold.structure["a"]["b"]["c"] == "0"
    assert len(scaffold.structure["a"]["b"]["c"]) == 1
    assert len(scaffold.structure["a"]["b"]) == 1
    assert len(scaffold.structure["a"]) == 1


def test_reject_file_without_file():
    # Given a defined structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # when someone tries to remvoe a file using the reject_file method
    # but one of its ancestor does not exist in the structure,
    scaffold.reject_file("x", path="a/b")
    # then the structure should be the same
    assert scaffold.structure["a"]["b"]["c"] == "0"
    assert len(scaffold.structure["a"]["b"]["c"]) == 1
    assert len(scaffold.structure["a"]["b"]) == 1
    assert len(scaffold.structure["a"]) == 1


def test_create_project_call_extension_hooks(tmpdir, git_mock):
    # Given an extension with hooks,
    called = []

    def extension(scaffold):
        scaffold.before_generate.append(lambda _: called.append('pre_hook'))
        scaffold.after_generate.append(lambda _: called.append('post_hook'))

    opts = get_default_opts("proj", extensions=[extension])

    # when created project is called,
    create_project(opts)

    # then the hooks should also be called.
    assert 'pre_hook' in called
    assert 'post_hook' in called


def test_create_project_generate_extension_files(tmpdir, git_mock):
    # Given a blank state,
    assert not path_exists("proj/tests/extra.file")
    assert not path_exists("proj/tests/another.file")

    # and an extension with extra files,
    def extension(scaffold):
        scaffold.ensure_file("extra.file", "content", path="proj/tests")
        scaffold.merge_structure(
            {"proj": {"tests": {"another.file": "content"}}})

    opts = get_default_opts("proj", extensions=[extension])

    # when the created project is called,
    create_project(opts)

    # then the files should be created
    assert path_exists("proj/tests/extra.file")
    assert tmpdir.join("proj/tests/extra.file").read() == "content"
    assert path_exists("proj/tests/another.file")
    assert tmpdir.join("proj/tests/another.file").read() == "content"


def test_create_project_respect_update_rules(tmpdir, git_mock):
    # Given an existing project
    opts = get_default_opts("proj")
    create_project(opts)
    for i in (0, 1, 3, 5, 6):
        tmpdir.ensure("proj/tests/file"+str(i)).write("old")
        assert path_exists("proj/tests/file"+str(i))

    # and an extension with extra files
    def extension(scaffold):
        nov, ncr = scaffold.NO_OVERWRITE, scaffold.NO_CREATE
        scaffold.ensure_file("file0", "new", path="proj/tests")
        scaffold.ensure_file("file1", "new", nov, path="proj/tests")
        scaffold.ensure_file("file2", "new", ncr, path="proj/tests")
        scaffold.merge_structure({"proj": {"tests": {"file3": ("new", nov),
                                                     "file4": ("new", ncr),
                                                     "file5": ("new", None),
                                                     "file6": "new"}}})

    opts = get_default_opts("proj", update=True, extensions=[extension])

    # When the created project is called,
    create_project(opts)

    # then the NO_CREATE files should not be created,
    assert not path_exists("proj/tests/file2")
    assert not path_exists("proj/tests/file4")
    # the NO_OVERWRITE files should not be updated
    assert tmpdir.join("proj/tests/file1").read() == "old"
    assert tmpdir.join("proj/tests/file3").read() == "old"
    # and files with no rules or `None` rules should be updated
    assert tmpdir.join("proj/tests/file0").read() == "new"
    assert tmpdir.join("proj/tests/file5").read() == "new"
    assert tmpdir.join("proj/tests/file6").read() == "new"


def test_api(tmpdir):  # noqa
    opts = get_default_opts('created_proj_with_api')
    create_project(opts)
    assert path_exists('created_proj_with_api')
    assert path_exists('created_proj_with_api/.git')
