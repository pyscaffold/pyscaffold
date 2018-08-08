#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re

from pyscaffold import structure, update

from .helpers import uniqstr


def test_apply_update_rules_to_file(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    NO_OVERWRITE = structure.FileOp.NO_OVERWRITE
    NO_CREATE = structure.FileOp.NO_CREATE

    # When update is False (no project exists yet) always update
    opts = {"update": False}
    res = update.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When content is string always update
    opts = {"update": True}
    res = update.apply_update_rule_to_file("a", "a", opts)
    assert res == "a"
    # When force is True always update
    opts = {"update": True, "force": True}
    res = update.apply_update_rule_to_file("a", ("a", NO_CREATE), opts)
    assert res == "a"
    # When file exist, update is True, rule is NO_OVERWRITE, do nothing
    opts = {"update": True}
    fname = uniqstr()
    tmpfolder.join(fname).write("content")
    res = update.apply_update_rule_to_file(
        fname, (fname, NO_OVERWRITE), opts)
    assert res is None
    logs = caplog.text
    assert re.search("skip.*" + fname, logs)
    # When file does not exist, update is True, but rule is NO_CREATE, do
    # nothing
    opts = {"update": True}
    fname = uniqstr()
    res = update.apply_update_rule_to_file(fname, (fname, NO_CREATE), opts)
    assert res is None
    assert re.search("skip.*" + fname, caplog.text)


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
    res_struct, _ = update.apply_update_rules(struct, opts)
    assert res_struct == exp_struct
