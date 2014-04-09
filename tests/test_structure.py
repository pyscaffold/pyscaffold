#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
from shutil import rmtree
from os.path import isfile, isdir

import pytest

from pyscaffold import structure


@pytest.yield_fixture()
def tmpdir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    rmtree(newpath)


def test_create_structure(tmpdir):
    struct = {"my_file": "Some content",
              "my_folder": {
                  "my_dir_file": "Some other content"
              },
              "empty_folder": {}
    }
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


# def test_make_structure():
#     assert True
#     args = type("Namespace", (object,), {"project": "project",
#                                           "package": "package"})
#     struct = structure.make_structure(args)
#     # assert True




