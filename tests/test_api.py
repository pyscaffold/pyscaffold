#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import exists as path_exists

import pytest
from pyscaffold import templates
from pyscaffold.api import Scaffold, create_project, get_default_opts
from pyscaffold.exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
    InvalidIdentifier
)


def test_merge_basics():
    # Given an existing structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "1",
                                                   "d": "2"}}})
    # when it is merged to another structure with some common folder
    extra_files = {"a": {"b": {"c": "0"},
                         "e": "2"},
                   "f": {"g": {"h": "0"}}}
    scaffold.merge(extra_files)
    # then the result, should contain both files from the original and the
    # merged structure,
    assert scaffold.structure["a"]["b"]["d"] == "2"
    assert scaffold.structure["f"]["g"]["h"] == "0"
    assert scaffold.structure["a"]["e"] == "2"
    # the common leaves should be overridden and a tuple (content, rule)
    assert scaffold.structure["a"]["b"]["c"] == ("0", None)


def test_merge_rules_just_in_original():
    # When an update rule exists in the original structure,
    scaffold = Scaffold({}, structure={"a": {"b": ("0", Scaffold.NO_CREATE)}})
    # but not in the merged,
    extra_files = {"a": {"b": "3"}}
    scaffold.merge(extra_files)
    # then just the content should be updated
    # and the rule should be kept identical
    assert scaffold.structure["a"]["b"] == ("3", Scaffold.NO_CREATE)


def test_merge_rules_just_in_merged():
    # When an update rule does not exist in the original structure,
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # but exists in the merged,
    extra_files = {"a": {"b": (None, Scaffold.NO_CREATE)}}
    scaffold.merge(extra_files)
    # then just the rule should be updated
    # and the content should be kept identical
    assert scaffold.structure["a"]["b"] == ("0", Scaffold.NO_CREATE)


def test_empty_string_ensure_empty_file_during_merge():
    # When the original structure contains a leaf,
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # and the merged structure overrides it with an empty content
    extra_files = {"a": {"b": ""}}
    scaffold.merge(extra_files)
    # then the resulting content should exist and be empty
    assert scaffold.structure["a"]["b"] == ("", None)


def test_ensure_nested():
    # When the original structure does not contain a leaf
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # that is added using the ensure method,
    scaffold.ensure("f", content="1", path=["a", "c", "d", "e"])
    # then all the necessary parent folder should be included
    assert isinstance(scaffold.structure["a"]["c"], dict)
    assert isinstance(scaffold.structure["a"]["c"]["d"], dict)
    assert isinstance(scaffold.structure["a"]["c"]["d"]["e"], dict)
    # and the file itself
    assert scaffold.structure["a"]["c"]["d"]["e"]["f"] == ("1", None)


def test_ensure_overriden():
    # When the original structure contains a leaf
    scaffold = Scaffold({}, structure={"a": {"b": "0"}})
    # that is overridden using the ensure method,
    scaffold.ensure("b", content="1", path=["a"])
    # and the file content should be overridden
    assert scaffold.structure["a"]["b"] == ("1", None)


def test_ensure_path():
    # When the ensure_path method is called with an string path
    scaffold = Scaffold({})
    scaffold.ensure("d", content="1", path="a/b/c")
    # Then the effect should be the same as if it were split
    assert scaffold.structure["a"]["b"]["c"]["d"] == ("1", None)


def test_reject():
    # When the original structure contain a leaf
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # that is removed using the reject method,
    scaffold.reject("c", path=["a", "b"])
    # then the structure should not contain the file
    assert "c" not in scaffold.structure["a"]["b"]


def test_reject_without_ancestor():
    # Given a defined structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # when someone tries to remvoe a file using the reject method
    # but one of its ancestor does not exist in the structure,
    scaffold.reject("c", path="a/b/x")
    # then the structure should be the same
    assert scaffold.structure["a"]["b"]["c"] == "0"
    assert len(scaffold.structure["a"]["b"]["c"]) == 1
    assert len(scaffold.structure["a"]["b"]) == 1
    assert len(scaffold.structure["a"]) == 1


def test_reject_without_file():
    # Given a defined structure,
    scaffold = Scaffold({}, structure={"a": {"b": {"c": "0"}}})
    # when someone tries to remvoe a file using the reject method
    # but one of its ancestor does not exist in the structure,
    scaffold.reject("x", path="a/b")
    # then the structure should be the same
    assert scaffold.structure["a"]["b"]["c"] == "0"
    assert len(scaffold.structure["a"]["b"]["c"]) == 1
    assert len(scaffold.structure["a"]["b"]) == 1
    assert len(scaffold.structure["a"]) == 1


def test_create_project_call_extension_hooks(tmpfolder, git_mock):
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


def test_create_project_generate_extension_files(tmpfolder, git_mock):
    # Given a blank state,
    assert not path_exists("proj/tests/extra.file")
    assert not path_exists("proj/tests/another.file")

    # and an extension with extra files,
    def extension(scaffold):
        scaffold.ensure("extra.file", "content", path="proj/tests")
        scaffold.merge(
            {"proj": {"tests": {"another.file": "content"}}})

    opts = get_default_opts("proj", extensions=[extension])

    # when the created project is called,
    create_project(opts)

    # then the files should be created
    assert path_exists("proj/tests/extra.file")
    assert tmpfolder.join("proj/tests/extra.file").read() == "content"
    assert path_exists("proj/tests/another.file")
    assert tmpfolder.join("proj/tests/another.file").read() == "content"


def test_create_project_respect_update_rules(tmpfolder, git_mock):
    # Given an existing project
    opts = get_default_opts("proj")
    create_project(opts)
    for i in (0, 1, 3, 5, 6):
        tmpfolder.ensure("proj/tests/file"+str(i)).write("old")
        assert path_exists("proj/tests/file"+str(i))

    # and an extension with extra files
    def extension(scaffold):
        nov, ncr = scaffold.NO_OVERWRITE, scaffold.NO_CREATE
        scaffold.ensure("file0", "new", path="proj/tests")
        scaffold.ensure("file1", "new", nov, path="proj/tests")
        scaffold.ensure("file2", "new", ncr, path="proj/tests")
        scaffold.merge({"proj": {"tests": {"file3": ("new", nov),
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
    assert tmpfolder.join("proj/tests/file1").read() == "old"
    assert tmpfolder.join("proj/tests/file3").read() == "old"
    # and files with no rules or `None` rules should be updated
    assert tmpfolder.join("proj/tests/file0").read() == "new"
    assert tmpfolder.join("proj/tests/file5").read() == "new"
    assert tmpfolder.join("proj/tests/file6").read() == "new"


def test_create_project_when_folder_exists(tmpfolder, git_mock):  # noqa
    tmpfolder.ensure("my-project", dir=True)
    opts = get_default_opts("my-project")
    with pytest.raises(DirectoryAlreadyExists):
        create_project(opts)
    opts = get_default_opts("my-project", force=True)
    create_project(opts)


def test_create_project_with_valid_package_name(tmpfolder, git_mock):  # noqa
    opts = get_default_opts("my-project", package="my_package")
    create_project(opts)


def test_create_project_with_invalid_package_name(tmpfolder, git_mock):  # noqa
    opts = get_default_opts("my-project", package="my:package")
    with pytest.raises(InvalidIdentifier):
        create_project(opts)


def test_create_project_when_updating(tmpfolder, git_mock):  # noqa
    opts = get_default_opts("my-project")
    create_project(opts)
    opts = get_default_opts("my-project", update=True)
    create_project(opts)
    assert path_exists("my-project")


def test_create_project_with_license(tmpfolder, git_mock):  # noqa
    opts = get_default_opts("my-project", license="new-bsd")
    create_project(opts)
    assert path_exists("my-project")
    content = tmpfolder.join("my-project/LICENSE.txt").read()
    assert content == templates.license(opts)


def test_create_project_with_namespaces(tmpfolder):  # noqa
    opts = get_default_opts("my-project", namespace="com.blue_yonder")
    create_project(opts)
    assert path_exists("my-project/com/blue_yonder/my_project")


def test_get_default_opts():
    opts = get_default_opts("project", package="package",
                            description="description")
    assert all(k in opts for k in "project update force author".split())
    assert isinstance(opts["extensions"], list)
    assert isinstance(opts["requirements"], list)


def test_get_default_opts_when_updating_project_doesnt_exist(tmpfolder, git_mock):  # noqa
    with pytest.raises(DirectoryDoesNotExist):
        get_default_opts("my-project", update=True)


def test_get_default_opts_when_updating_with_wrong_setup(tmpfolder, git_mock):  # noqa
    tmpfolder.ensure("my-project", dir=True)
    tmpfolder.join("my-project/setup.py").write('a')
    with pytest.raises(RuntimeError):
        get_default_opts("my-project", update=True)


def test_get_default_opts_with_nogit(nogit_mock):  # noqa
    with pytest.raises(GitNotInstalled):
        get_default_opts("my-project")


def test_get_default_opts_with_git_not_configured(noconfgit_mock):  # noqa
    with pytest.raises(GitNotConfigured):
        get_default_opts("my-project")


def test_api(tmpfolder):  # noqa
    opts = get_default_opts('created_proj_with_api')
    create_project(opts)
    assert path_exists('created_proj_with_api')
    assert path_exists('created_proj_with_api/.git')
