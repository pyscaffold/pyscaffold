#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import isfile, isdir

import pytest

from pyscaffold import structure

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


def test_make_structure():
    args = type("Namespace", (), {"project": "project",
                                  "package": "package",
                                  "description": "description"})
    struct = structure.make_structure(args)
    assert isinstance(struct, dict)
