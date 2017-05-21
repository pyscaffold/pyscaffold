#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import isdir, isfile

import pytest
from pyscaffold import api, cli, structure, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_create_structure(tmpdir):  # noqa
    struct = {"my_file": "Some content",
              "my_folder": {
                  "my_dir_file": "Some other content",
                  "empty_file": "",
                  "file_not_created": None
              },
              "empty_folder": {}}
    expected = {"my_file": "Some content",
                "my_folder": {
                    "my_dir_file": "Some other content",
                    "empty_file": ""
                },
                "empty_folder": {}}
    changed = structure.create_structure(struct)

    assert changed == expected
    assert isdir("my_folder")
    assert isdir("empty_folder")
    assert isfile("my_folder/my_dir_file")
    assert isfile("my_folder/empty_file")
    assert not isfile("my_folder/file_not_created")
    assert isfile("my_file")
    assert open("my_file").read() == "Some content"
    assert open("my_folder/my_dir_file").read() == "Some other content"
    assert open("my_folder/empty_file").read() == ""


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
    opts = api.get_default_opts(opts['project'], **opts)
    struct = structure.make_structure(opts)
    assert isinstance(struct, dict)


def test_apply_update_rules_to_file(tmpdir):
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE

    # When update is False (no project exists yet) always update
    opts = {"update": False}
    res = structure.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When content is string always update
    opts = {"update": True}
    res = structure.apply_update_rule_to_file("a", "a", opts)
    assert res == "a"
    # When force is True always update
    opts = {"update": True, "force": True}
    res = structure.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When file exist, update is True, rule is NO_OVERWRITE, do nothing
    opts = {"update": True}
    tmpdir.join("a").write("content")
    res = structure.apply_update_rule_to_file("a", ("a", NO_OVERWRITE), opts)
    assert res is None
    # When file does not exist, update is True, but rule is NO_CREATE, do
    # nothing
    opts = {"update": True}
    res = structure.apply_update_rule_to_file("b", ("b", NO_CREATE), opts)
    assert res is None


def test_apply_update_rules(tmpdir):  # noqa
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE
    opts = dict(update=True)

    struct = {"a": ("a", NO_OVERWRITE),
              "b": "b",
              "c": {"a": "a",
                    "b": ("b", NO_OVERWRITE)},
              "d": {"a": ("a", NO_OVERWRITE),
                    "b": ("b", NO_CREATE)},
              "e": ("e", NO_CREATE)}
    dir_struct = {"a": "a",
                  "c": {"b": "b"}}
    exp_struct = {"b": "b",
                  "c": {"a": "a"},
                  "d": {"a": "a"}}
    structure.create_structure(dir_struct)
    res_struct = structure.apply_update_rules(struct, opts)
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
