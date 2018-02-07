#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from os.path import isdir, isfile

import pytest

from pyscaffold import api, cli, structure

from .log_helpers import last_log


def test_create_structure(tmpfolder):
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
    changed, _ = structure.create_structure(struct, {})

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


def test_create_structure_with_wrong_type(tmpfolder):
    with pytest.raises(RuntimeError):
        struct = {"strange_thing": 1}
        structure.create_structure(struct, {})


def test_create_structure_when_updating(tmpfolder):
    struct = {"my_file": "Some content",
              "my_folder": {
                  "my_dir_file": "Some other content"
              },
              "empty_folder": {}}
    structure.create_structure(struct, dict(update=False))
    struct["my_folder"]["my_dir_file"] = "Changed content"
    structure.create_structure(struct, dict(update=True))
    with open("my_folder/my_dir_file") as fh:
        assert fh.read() == "Changed content"


def test_create_structure_when_dir_exists(tmpfolder):
    struct = {"my_folder": {"my_dir_file": "Some other content"}}
    os.mkdir("my_folder")
    with pytest.raises(OSError):
        structure.create_structure(struct, dict(update=False))


def test_define_structure():
    args = ["project", "-p", "package", "-d", "description"]
    opts = cli.parse_args(args)
    _, opts = api.get_default_options({}, opts)
    struct, _ = structure.define_structure({}, opts)
    assert isinstance(struct, dict)


def test_apply_update_rules_to_file(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
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
    tmpfolder.join("a").write("content")
    res = structure.apply_update_rule_to_file("a", ("a", NO_OVERWRITE), opts)
    assert res is None
    assert "skip  a" in last_log(caplog)
    # When file does not exist, update is True, but rule is NO_CREATE, do
    # nothing
    opts = {"update": True}
    res = structure.apply_update_rule_to_file("b", ("b", NO_CREATE), opts)
    assert res is None
    assert "skip  b" in last_log(caplog)


def test_apply_update_rules(tmpfolder):
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
    structure.create_structure(dir_struct, opts)
    res_struct, _ = structure.apply_update_rules(struct, opts)
    assert res_struct == exp_struct
