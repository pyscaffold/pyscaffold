#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import isdir, isfile

import pytest
import six
from pyscaffold import cli, structure, utils

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
    opts = cli.parse_args(args)
    opts = cli.get_default_opts(opts['project'], **opts)
    struct = structure.make_structure(opts)
    assert isinstance(struct, dict)


def test_create_django_project_no_django(nodjango_admin_mock):  # noqa
    args = ["project", "-p", "package", "-d", "description"]
    opts = cli.parse_args(args)
    with pytest.raises(RuntimeError):
        structure.create_django_proj(opts)


def test_make_structure_with_pre_commit_hooks():
    args = ["project",
            "-p", "package",
            "-d", "description",
            "--with-pre-commit"]
    opts = cli.parse_args(args)
    opts = cli.get_default_opts(opts['project'], **opts)
    struct = structure.make_structure(opts)
    assert isinstance(struct, dict)
    assert ".pre-commit-config.yaml" in struct["project"]


def test_make_structure_with_tox():
    args = ["project",
            "-p", "package",
            "-d", "description",
            "--with-tox"]
    opts = cli.parse_args(args)
    opts = cli.get_default_opts(opts['project'], **opts)
    struct = structure.make_structure(opts)
    assert isinstance(struct, dict)
    assert "tox.ini" in struct["project"]
    assert isinstance(struct["project"]["tox.ini"], six.string_types)


def test_apply_update_rules(tmpdir):  # noqa
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE
    rules = {"a": NO_OVERWRITE,
             "c": {"b": NO_OVERWRITE},
             "d": {"a": NO_OVERWRITE,
                   "b": NO_CREATE,
                   "c": NO_CREATE,
                   "d": NO_OVERWRITE},
             "e": NO_CREATE}
    struct = {"a": "a",
              "b": "b",
              "c": {"a": "a",
                    "b": "b"},
              "d": {"a": "a",
                    "b": "b"},
              "e": "e"}
    dir_struct = {"a": "a",
                  "c": {"b": "b"}}
    exp_struct = {"b": "b",
                  "c": {"a": "a"},
                  "d": {"a": "a"}}
    structure.create_structure(dir_struct)
    res_struct = structure.apply_update_rules(rules, struct)
    assert res_struct == exp_struct


def test_add_namespace():
    args = ["project",
            "-p", "package",
            "--with-namespace", "com.blue_yonder"]
    opts = cli.parse_args(args)
    opts['namespace'] = utils.prepare_namespace(opts['namespace'])
    struct = {"project": {"package": {"file1": "Content"}}}
    ns_struct = structure.add_namespace(opts, struct)
    assert ["project"] == list(ns_struct.keys())
    assert "package" not in list(ns_struct.keys())
    assert ["com"] == list(ns_struct["project"].keys())
    assert {"blue_yonder", "__init__.py"} == set(
        ns_struct["project"]["com"].keys())
    assert "package" in list(ns_struct["project"]["com"]["blue_yonder"].keys())
