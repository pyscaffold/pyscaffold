from pathlib import Path

import pytest

from pyscaffold.actions import discover, get_default_options, verify_project_dir
from pyscaffold.api import bootstrap_options
from pyscaffold.exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
)


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
