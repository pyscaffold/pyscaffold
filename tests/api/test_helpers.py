import pytest

from pyscaffold import actions
from pyscaffold.api import helpers
from pyscaffold.exceptions import ActionNotFound
from pyscaffold.structure import define_structure


def custom_action(structure, options):
    return structure, options


custom_action.__module__ = "awesome_module"


def init_git(structure, options):
    """Fake action that shares the same name as a default action."""
    return structure, options


def test_register_before():
    # Given an action list,
    pipeline = [actions.init_git]
    # When a new action is registered before another, using the function name
    # as position reference,
    pipeline = helpers.register(pipeline, custom_action, before="init_git")
    # Then this action should be correctly placed
    assert pipeline == [custom_action, actions.init_git]


def test_register_after():
    # Given an action list,
    pipeline = [actions.init_git]
    # When a new action is registered after another, using the function name
    # as position reference,
    pipeline = helpers.register(pipeline, custom_action, after="init_git")
    # Then this action should be correctly placed
    assert pipeline == [actions.init_git, custom_action]


def test_register_with_qualified_name():
    # Given an action list with actions that share the same name,
    pipeline = [actions.init_git, init_git]
    # When a new action is registered using the "qualified" name
    # (module+function) as position reference,
    position = "pyscaffold.actions:init_git"
    pipeline = helpers.register(pipeline, custom_action, after=position)
    # Then this action should be correctly placed
    assert pipeline == [actions.init_git, custom_action, init_git]


def test_register_default_position():
    # Given an action list with define_structure,
    pipeline = [actions.init_git, define_structure, init_git]
    # When a new action is registered without position reference,
    pipeline = helpers.register(pipeline, custom_action)
    # Then this action should be placed after define_structure
    assert pipeline == [actions.init_git, define_structure, custom_action, init_git]


def test_register_with_invalid_reference():
    # Given an action list,
    pipeline = [actions.init_git]
    # When a new action is registered using an invalid reference,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        pipeline = helpers.register(pipeline, custom_action, after="undefined_action")
    # And the action list should remain the same
    assert pipeline == [actions.init_git]


def test_unregister():
    # Given an action list with name conflict,
    pipeline = [custom_action, init_git, actions.init_git]
    # When an action is unregistered by name,
    pipeline = helpers.unregister(pipeline, "init_git")
    # Then the first match should be removed
    assert pipeline == [custom_action, actions.init_git]


def test_unregister_with_qualified_name():
    # Given an action list with name conflict,
    pipeline = [custom_action, init_git, actions.init_git]
    # When an action is unregistered by "qualified" name,
    pipeline = helpers.unregister(pipeline, "pyscaffold.actions:init_git")
    # Then the correct match should be removed
    assert pipeline == [custom_action, init_git]


def test_unregister_with_undefined_action():
    # Given an action list,
    pipeline = [actions.init_git]
    # When a undefined action is unregistered,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        pipeline = helpers.unregister(pipeline, "undefined_action")
    # And the action list should remain the same
    assert pipeline == [actions.init_git]
