from os.path import isdir, isfile
from pathlib import Path

import pytest

from pyscaffold import actions, api, cli, operations, structure

NO_OVERWRITE = operations.no_overwrite()
SKIP_ON_UPDATE = operations.skip_on_update()


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
    with pytest.raises(TypeError):
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


def test_create_structure_create_project_folder(tmpfolder):
    struct = {"my_folder": {"my_dir_file": "Some other content"}}
    opts = dict(project_path="my_project", update=False)
    structure.create_structure(struct, opts)
    assert isdir("my_project")


def test_define_structure():
    args = ["project", "-p", "package", "-d", "description"]
    opts = cli.parse_args(args)
    opts = api.bootstrap_options(opts)
    _, opts = actions.get_default_options({}, opts)
    struct, _ = structure.define_structure({}, opts)
    assert isinstance(struct, dict)


def test_merge_basics():
    # Given an existing struct,
    struct = {"a": {"b": {"c": "1", "d": "2"}}}
    # when it is merged to another struct with some common folder
    extra_files = {"a": {"b": {"c": "0"}, "e": "2"}, "f": {"g": {"h": "0"}}}
    struct = structure.merge(struct, extra_files)
    # then the result, should contain both files from the original and the
    # merged struct,
    assert struct["a"]["b"]["d"] == "2"
    assert struct["f"]["g"]["h"] == "0"
    assert struct["a"]["e"] == "2"
    # the common leaves should be overridden and a tuple (content, rule)
    assert struct["a"]["b"]["c"] == "0"


def test_merge_rules_just_in_original():
    # When an update rule exists in the original struct,
    struct = {"a": {"b": ("0", SKIP_ON_UPDATE)}}
    # but not in the merged,
    extra_files = {"a": {"b": "3"}}
    struct = structure.merge(struct, extra_files)
    # then just the content should be updated
    # and the rule should be kept identical
    assert struct["a"]["b"] == ("3", SKIP_ON_UPDATE)


def test_merge_rules_just_in_merged():
    # When an update rule does not exist in the original struct,
    struct = {"a": {"b": "0"}}
    # but exists in the merged,
    extra_files = {"a": {"b": (None, SKIP_ON_UPDATE)}}
    struct = structure.merge(struct, extra_files)
    # then just the rule should be updated
    # and the content should be kept identical
    assert struct["a"]["b"] == ("0", SKIP_ON_UPDATE)


def test_empty_string_leads_to_empty_file_during_merge():
    # When the original struct contains a leaf,
    struct = {"a": {"b": "0"}}
    # and the merged struct overrides it with an empty content
    extra_files = {"a": {"b": ""}}
    struct = structure.merge(struct, extra_files)
    # then the resulting content should exist and be empty
    assert struct["a"]["b"] == ""


def test_modify_non_existent():
    # Given the original struct does not contain a leaf
    # that is targeted by the modify method,
    struct = {"a": {"b": "0"}}

    # When the modify is called
    # Then the argument passed should be None
    def _modifier(old, op):
        assert old is None
        return ("1", op)

    struct = structure.modify(struct, Path("a", "c"), _modifier)

    # But the result of the modifier function should be included in the tree
    assert struct["a"]["c"] == ("1", operations.create)


def test_modify_file_op():
    struct = {"a": {"b": "0"}}
    struct = structure.modify(struct, "a/b", lambda text, _: (text, SKIP_ON_UPDATE))
    assert struct["a"]["b"] == ("0", SKIP_ON_UPDATE)


def test_ensure_nested():
    # When the original struct does not contain a leaf
    struct = {"a": {"b": "0"}}
    # that is added using the ensure method,
    struct = structure.ensure(struct, Path("a", "c", "d", "e", "f"), content="1")
    # then all the necessary parent folder should be included
    assert isinstance(struct["a"]["c"], dict)
    assert isinstance(struct["a"]["c"]["d"], dict)
    assert isinstance(struct["a"]["c"]["d"]["e"], dict)
    # and the file itself
    assert struct["a"]["c"]["d"]["e"]["f"] == ("1", operations.create)


def test_ensure_overriden():
    # When the original struct contains a leaf
    struct = {"a": {"b": "0"}}
    # that is overridden using the ensure method,
    struct = structure.ensure(struct, Path("a", "b"), content="1")
    # and the file content should be overridden
    assert struct["a"]["b"] == ("1", operations.create)


def test_ensure_path():
    # When the ensure method is called with an string path
    struct = {}
    struct = structure.ensure(struct, "a/b/c/d", content="1")
    # Then the effect should be the same as if it were split
    assert struct["a"]["b"]["c"]["d"] == ("1", operations.create)


def test_ensure_file_op():
    # When the ensure method is called with a file_op and no content
    struct = {"a": {"b": "0"}}
    struct = structure.ensure(struct, "a/b", file_op=NO_OVERWRITE)
    # Then the content should remain the same
    # But the file_op should change
    assert struct["a"]["b"] == ("0", NO_OVERWRITE)


def test_reject():
    # When the original struct contain a leaf
    struct = {"a": {"b": {"c": "0"}}}
    # that is removed using the reject method,
    struct = structure.reject(struct, Path("a", "b", "c"))
    # then the struct should not contain the file
    assert "c" not in struct["a"]["b"]


def test_reject_without_ancestor():
    # Given a defined struct,
    struct = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the struct,
    struct = structure.reject(struct, "a/b/x/c")
    # then the struct should be the same
    assert struct["a"]["b"]["c"] == "0"
    assert len(struct["a"]["b"]["c"]) == 1
    assert len(struct["a"]["b"]) == 1
    assert len(struct["a"]) == 1


def test_reject_without_file():
    # Given a defined struct,
    struct = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the struct,
    struct = structure.reject(struct, "a/b/x")
    # then the struct should be the same
    assert struct["a"]["b"]["c"] == "0"
    assert len(struct["a"]["b"]["c"]) == 1
    assert len(struct["a"]["b"]) == 1
    assert len(struct["a"]) == 1
