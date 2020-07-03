# -*- coding: utf-8 -*-
import os
from os.path import isdir, isfile

import pytest

from pyscaffold import api, cli, structure


def test_create_structure(tmpfolder):
    struct = {
        "my_file": "Some content",
        "my_folder": {
            "my_dir_file": "Some other content",
            "empty_file": "",
            "file_not_created": None,
        },
        "empty_folder": {},
    }
    expected = {
        "my_file": "Some content",
        "my_folder": {"my_dir_file": "Some other content", "empty_file": ""},
        "empty_folder": {},
    }
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
    struct = {
        "my_file": "Some content",
        "my_folder": {"my_dir_file": "Some other content"},
        "empty_folder": {},
    }
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
