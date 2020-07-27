from pathlib import Path

import pytest

from pyscaffold.actions import discover, get_default_options
from pyscaffold.actions import init_git as orig_init_git
from pyscaffold.actions import register, unregister, verify_project_dir
from pyscaffold.api import bootstrap_options
from pyscaffold.exceptions import (
    ActionNotFound,
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
)
from pyscaffold.structure import define_structure


def test_discover():
    # Given an extension with actions,
    def fake_action(struct, opts):
        return struct, opts

    def extension(actions):
        return [fake_action] + actions

    # When discover is called,
    actions = discover([extension])

    # Then the extension actions should be listed alongside default actions.
    assert get_default_options in actions
    assert fake_action in actions


def test_get_default_opts():
    opts = bootstrap_options(project_path="project", package="package")
    _, opts = get_default_options({}, opts)
    assert all(k in opts for k in "project_path update force author".split())
    assert isinstance(opts["extensions"], list)
    assert isinstance(opts["requirements"], list)


def test_get_default_opts_with_nogit(nogit_mock):
    with pytest.raises(GitNotInstalled):
        get_default_options({}, dict(project_path="my-project"))


def test_get_default_opts_with_git_not_configured(noconfgit_mock):
    with pytest.raises(GitNotConfigured):
        get_default_options({}, dict(project_path="my-project"))


def test_verify_project_dir_when_project_doesnt_exist_and_updating(tmpfolder, git_mock):
    opts = dict(project_path=Path("my-project"), update=True)
    with pytest.raises(DirectoryDoesNotExist):
        verify_project_dir({}, opts)


def test_verify_project_dir_when_project_exist_but_not_updating(tmpfolder, git_mock):
    tmpfolder.ensure("my-project", dir=True)
    opts = dict(project_path=Path("my-project"), update=False, force=False)
    with pytest.raises(DirectoryAlreadyExists):
        verify_project_dir({}, opts)


def custom_action(structure, options):
    return structure, options


custom_action.__module__ = "awesome_module"


def init_git(structure, options):
    """Fake action that shares the same name as a default action."""
    return structure, options


def test_register_before():
    # Given an action list,
    pipeline = [orig_init_git]
    # When a new action is registered before another, using the function name
    # as position reference,
    pipeline = register(pipeline, custom_action, before="init_git")
    # Then this action should be correctly placed
    assert pipeline == [custom_action, orig_init_git]


def test_register_after():
    # Given an action list,
    pipeline = [orig_init_git]
    # When a new action is registered after another, using the function name
    # as position reference,
    pipeline = register(pipeline, custom_action, after="init_git")
    # Then this action should be correctly placed
    assert pipeline == [orig_init_git, custom_action]


def test_register_with_qualified_name():
    # Given an action list with actions that share the same name,
    pipeline = [orig_init_git, init_git]
    # When a new action is registered using the "qualified" name
    # (module+function) as position reference,
    position = "pyscaffold.actions:init_git"
    pipeline = register(pipeline, custom_action, after=position)
    # Then this action should be correctly placed
    assert pipeline == [orig_init_git, custom_action, init_git]


def test_register_default_position():
    # Given an action list with define_structure,
    pipeline = [orig_init_git, define_structure, init_git]
    # When a new action is registered without position reference,
    pipeline = register(pipeline, custom_action)
    # Then this action should be placed after define_structure
    assert pipeline == [orig_init_git, define_structure, custom_action, init_git]


def test_register_with_invalid_reference():
    # Given an action list,
    pipeline = [orig_init_git]
    # When a new action is registered using an invalid reference,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        pipeline = register(pipeline, custom_action, after="undefined_action")
    # And the action list should remain the same
    assert pipeline == [orig_init_git]


def test_unregister():
    # Given an action list with name conflict,
    pipeline = [custom_action, init_git, orig_init_git]
    # When an action is unregistered by name,
    pipeline = unregister(pipeline, "init_git")
    # Then the first match should be removed
    assert pipeline == [custom_action, orig_init_git]


def test_unregister_with_qualified_name():
    # Given an action list with name conflict,
    pipeline = [custom_action, init_git, orig_init_git]
    # When an action is unregistered by "qualified" name,
    pipeline = unregister(pipeline, "pyscaffold.actions:init_git")
    # Then the correct match should be removed
    assert pipeline == [custom_action, init_git]


def test_unregister_with_undefined_action():
    # Given an action list,
    pipeline = [orig_init_git]
    # When a undefined action is unregistered,
    with pytest.raises(ActionNotFound):
        # Then the proper exception should be raised,
        pipeline = unregister(pipeline, "undefined_action")
    # And the action list should remain the same
    assert pipeline == [orig_init_git]
