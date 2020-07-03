#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import PurePath as Path

import pytest

from pyscaffold import api
from pyscaffold.api import helpers
from pyscaffold.exceptions import ActionNotFound
from pyscaffold.structure import define_structure


def test_merge_basics():
    # Given an existing structure,
    structure = {"a": {"b": {"c": "1", "d": "2"}}}
    # when it is merged to another structure with some common folder
    extra_files = {"a": {"b": {"c": "0"}, "e": "2"}, "f": {"g": {"h": "0"}}}
    structure = helpers.merge(structure, extra_files)
    # then the result, should contain both files from the original and the
    # merged structure,
    assert structure["a"]["b"]["d"] == "2"
    assert structure["f"]["g"]["h"] == "0"
    assert structure["a"]["e"] == "2"
    # the common leaves should be overridden and a tuple (content, rule)
    assert structure["a"]["b"]["c"] == "0"


def test_merge_rules_just_in_original():
    # When an update rule exists in the original structure,
    structure = {"a": {"b": ("0", helpers.NO_CREATE)}}
    # but not in the merged,
    extra_files = {"a": {"b": "3"}}
    structure = helpers.merge(structure, extra_files)
    # then just the content should be updated
    # and the rule should be kept identical
    assert structure["a"]["b"] == ("3", helpers.NO_CREATE)


def test_merge_rules_just_in_merged():
    # When an update rule does not exist in the original structure,
    structure = {"a": {"b": "0"}}
    # but exists in the merged,
    extra_files = {"a": {"b": (None, helpers.NO_CREATE)}}
    structure = helpers.merge(structure, extra_files)
    # then just the rule should be updated
    # and the content should be kept identical
    assert structure["a"]["b"] == ("0", helpers.NO_CREATE)


def test_empty_string_leads_to_empty_file_during_merge():
    # When the original structure contains a leaf,
    structure = {"a": {"b": "0"}}
    # and the merged structure overrides it with an empty content
    extra_files = {"a": {"b": ""}}
    structure = helpers.merge(structure, extra_files)
    # then the resulting content should exist and be empty
    assert structure["a"]["b"] == ""


def test_modify_non_existent():
    # Given the original structure does not contain a leaf
    # that is targeted by the modify method,
    structure = {"a": {"b": "0"}}

    # When the modify is called
    # Then the argument passed should be None
    def _modifier(old):
        assert old is None
        return "1"

    structure = helpers.modify(structure, Path("a", "c"), _modifier)

    # But the result of the modifier function should be included in the tree
    assert structure["a"]["c"] == "1"


def test_modify_no_function():
    # Given a structure
    structure = {"a": {"b": "0"}}

    # When the modify helper is called with an update rule but no modifier
    structure = helpers.modify(structure, "a/b", update_rule=helpers.NO_CREATE)

    # Then the content should remain the same
    # But the flag should change
    assert structure["a"]["b"] == ("0", helpers.NO_CREATE)


def test_ensure_nested():
    # When the original structure does not contain a leaf
    structure = {"a": {"b": "0"}}
    # that is added using the ensure method,
    structure = helpers.ensure(structure, Path("a", "c", "d", "e", "f"), content="1")
    # then all the necessary parent folder should be included
    assert isinstance(structure["a"]["c"], dict)
    assert isinstance(structure["a"]["c"]["d"], dict)
    assert isinstance(structure["a"]["c"]["d"]["e"], dict)
    # and the file itself
    assert structure["a"]["c"]["d"]["e"]["f"] == "1"


def test_ensure_overriden():
    # When the original structure contains a leaf
    structure = {"a": {"b": "0"}}
    # that is overridden using the ensure method,
    structure = helpers.ensure(structure, Path("a", "b"), content="1")
    # and the file content should be overridden
    assert structure["a"]["b"] == "1"


def test_ensure_path():
    # When the ensure method is called with an string path
    structure = {}
    structure = helpers.ensure(structure, "a/b/c/d", content="1")
    # Then the effect should be the same as if it were split
    assert structure["a"]["b"]["c"]["d"] == "1"


def test_reject():
    # When the original structure contain a leaf
    structure = {"a": {"b": {"c": "0"}}}
    # that is removed using the reject method,
    structure = helpers.reject(structure, Path("a", "b", "c"))
    # then the structure should not contain the file
    assert "c" not in structure["a"]["b"]


def test_reject_without_ancestor():
    # Given a defined structure,
    structure = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the structure,
    structure = helpers.reject(structure, "a/b/x/c")
    # then the structure should be the same
    assert structure["a"]["b"]["c"] == "0"
    assert len(structure["a"]["b"]["c"]) == 1
    assert len(structure["a"]["b"]) == 1
    assert len(structure["a"]) == 1


def test_reject_without_file():
    # Given a defined structure,
    structure = {"a": {"b": {"c": "0"}}}
    # when someone tries to remove a file using the reject method
    # but one of its ancestor does not exist in the structure,
    structure = helpers.reject(structure, "a/b/x")
    # then the structure should be the same
    assert structure["a"]["b"]["c"] == "0"
    assert len(structure["a"]["b"]["c"]) == 1
    assert len(structure["a"]["b"]) == 1
    assert len(structure["a"]) == 1


def custom_action(structure, options):
    return structure, options


custom_action.__module__ = "awesome_module"


def init_git(structure, options):
    """Fake action that shares the same name as a default action."""
    return structure, options


def test_register_before():
    # Given an action list,
    actions = [api.init_git]
    # When a new action is registered before another, using the function name
    # as position reference,
    actions = helpers.register(actions, custom_action, before="init_git")
    # Then this action should be correctly placed
    assert actions == [custom_action, api.init_git]


def test_register_after():
    # Given an action list,
    actions = [api.init_git]
    # When a new action is registered after another, using the function name
    # as position reference,
    actions = helpers.register(actions, custom_action, after="init_git")
    # Then this action should be correctly placed
    assert actions == [api.init_git, custom_action]


def test_register_with_qualified_name():
    # Given an action list with actions that share the same name,
    actions = [api.init_git, init_git]
    # When a new action is registered using the "qualified" name
    # (module+function) as position reference,
    actions = helpers.register(actions, custom_action, after="pyscaffold.api:init_git")
    # Then this action should be correctly placed
    assert actions == [api.init_git, custom_action, init_git]


def test_register_default_position():
    # Given an action list with define_structure,
    actions = [api.init_git, define_structure, init_git]
    # When a new action is registered without position reference,
    actions = helpers.register(actions, custom_action)
    # Then this action should be placed after define_structure
    assert actions == [api.init_git, define_structure, custom_action, init_git]


def test_register_with_invalid_reference():
    # Given an action list,
    actions = [api.init_git]
    # When a new action is registered using an invalid reference,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        actions = helpers.register(actions, custom_action, after="undefined_action")
    # And the action list should remain the same
    assert actions == [api.init_git]


def test_unregister():
    # Given an action list with name conflict,
    actions = [custom_action, init_git, api.init_git]
    # When an action is unregistered by name,
    actions = helpers.unregister(actions, "init_git")
    # Then the first match should be removed
    assert actions == [custom_action, api.init_git]


def test_unregister_with_qualified_name():
    # Given an action list with name conflict,
    actions = [custom_action, init_git, api.init_git]
    # When an action is unregistered by "qualified" name,
    actions = helpers.unregister(actions, "pyscaffold.api:init_git")
    # Then the correct match should be removed
    assert actions == [custom_action, init_git]


def test_unregister_with_undefined_action():
    # Given an action list,
    actions = [api.init_git]
    # When a undefined action is unregistered,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        actions = helpers.unregister(actions, "undefined_action")
    # And the action list should remain the same
    assert actions == [api.init_git]
