#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import isdir, isfile

import pytest
from pyscaffold import runner, structure

from .fixtures import nodjango_admin_mock, tmpdir

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_create_structure(tmpdir):
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


def test_create_structure_with_wrong_type(tmpdir):
    with pytest.raises(RuntimeError):
        struct = {"strange_thing": 1}
        structure.create_structure(struct)


def test_create_structure_when_updating(tmpdir):
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


def test_create_structure_when_dir_exists(tmpdir):
    struct = {"my_folder": {"my_dir_file": "Some other content"}}
    os.mkdir("my_folder")
    with pytest.raises(OSError):
        structure.create_structure(struct, update=False)


def test_make_structure():
    args = ["project", "-p", "package", "-d", "description"]
    args = runner.parse_args(args)
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)


def test_set_default_args():
    args = ["project", "-p", "package", "-d", "description"]
    args = runner.parse_args(args)
    new_args = structure.set_default_args(args)
    assert not hasattr(args, "author")
    assert hasattr(new_args, "author")


def test_create_django_project(nodjango_admin_mock):
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
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)
    assert ".pre-commit-config.yaml" in struct["project"]
