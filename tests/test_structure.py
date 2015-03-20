#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import isdir, isfile

import pytest
import six
from pyscaffold import runner, structure

from .fixtures import nodjango_admin_mock, tmpdir  # noqa

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_create_structure(tmpdir):  # noqa
    struct = {"my_file": "Some content",
              "my_folder": {
                  "my_dir_file": "Some other content"
              },
              "empty_folder": {}}
    structure.create_structure(struct)

    assert isdir("my_folder")
    assert isdir("empty_folder")
    assert isfile("my_folder/my_dir_file")
    assert isfile("my_file")
    assert open("my_file").read() == "Some content"
    assert open("my_folder/my_dir_file").read() == "Some other content"


def test_create_structure_with_wrong_type(tmpdir):  # noqa
    with pytest.raises(RuntimeError):
        struct = {"strange_thing": 1}
        structure.create_structure(struct)


def test_create_structure_when_updating(tmpdir):  # noqa
    struct = {"my_file": "Some content",
              "my_folder": {
                  "my_dir_file": "Some other content"
              },
              "empty_folder": {}}
    structure.create_structure(struct, update=False)
    struct["my_folder"]["my_dir_file"] = "Changed content"
    structure.create_structure(struct, update=True)
    with open("my_folder/my_dir_file") as fh:
        assert fh.read() == "Changed content"


def test_create_structure_when_dir_exists(tmpdir):  # noqa
    struct = {"my_folder": {"my_dir_file": "Some other content"}}
    os.mkdir("my_folder")
    with pytest.raises(OSError):
        structure.create_structure(struct, update=False)


def test_make_structure():
    args = ["project", "-p", "package", "-d", "description"]
    args = runner.parse_args(args)
    args = structure.set_default_args(args)
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)


def test_set_default_args():
    args = ["project", "-p", "package", "-d", "description"]
    args = runner.parse_args(args)
    new_args = structure.set_default_args(args)
    assert not hasattr(args, "author")
    assert hasattr(new_args, "author")


def test_create_django_project(nodjango_admin_mock):  # noqa
    args = ["project", "-p", "package", "-d", "description"]
    args = runner.parse_args(args)
    with pytest.raises(RuntimeError):
        structure.create_django_proj(args)


def test_make_structure_with_pre_commit_hooks():
    args = ["project",
            "-p", "package",
            "-d", "description",
            "--with-pre-commit"]
    args = runner.parse_args(args)
    args = structure.set_default_args(args)
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)
    assert ".pre-commit-config.yaml" in struct["project"]


def test_make_structure_with_tox():
    args = ["project",
            "-p", "package",
            "-d", "description",
            "--with-tox"]
    args = runner.parse_args(args)
    args = structure.set_default_args(args)
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)
    assert "tox.ini" in struct["project"]
    assert isinstance(struct["project"]["tox.ini"], six.string_types)


def test_check_files_exist(tmpdir):  # noqa
    struct = {"a": "a", "b": "b", "c": {"a": "a", "b": "b"}, "d": {"a": "a"}}
    dir_struct = {"a": "a", "c": {"b": "b"}}
    structure.create_structure(dir_struct)
    res = structure.check_files_exist(struct)
    assert res == dir_struct


def test_remove_from_struct():
    orig_struct = {"a": 1, "b": 2, "c": 3}
    del_struct = {"a": 1}
    res = structure.remove_from_struct(orig_struct, del_struct)
    assert res == {"b": 2, "c": 3}
    orig_struct = {"a": 1, "b": 2, "c": {"a": 1}}
    del_struct = {"a": 1}
    res = structure.remove_from_struct(orig_struct, del_struct)
    assert res == {"b": 2, "c": {"a": 1}}
    orig_struct = {"a": 1, "b": 2, "c": {"a": 1}}
    del_struct = {"c": {"a": 1}}
    res = structure.remove_from_struct(orig_struct, del_struct)
    assert res == {"a": 1, "b": 2}
    orig_struct = {"a": 1, "b": 2, "c": {"a": 1, "b": 2}}
    del_struct = {"a": 1, "c": {"a": 1}}
    res = structure.remove_from_struct(orig_struct, del_struct)
    assert res == {"b": 2, "c": {"b": 2}}


def test_add_namespace():
    args = ["project",
            "-p", "package",
            "--with-namespace", "com.blue_yonder"]
    args = runner.parse_args(args)
    args.namespace = runner.prepare_namespace(args.namespace)
    struct = {"project": {"package": {"file1": "Content"}}}
    ns_struct = structure.add_namespace(args, struct)
    assert ["project"] == list(ns_struct.keys())
    assert "package" not in list(ns_struct.keys())
    assert ["com"] == list(ns_struct["project"].keys())
    assert {"blue_yonder", "__init__.py"} == set(
        ns_struct["project"]["com"].keys())
    assert "package" in list(ns_struct["project"]["com"]["blue_yonder"].keys())
