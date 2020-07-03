# -*- coding: utf-8 -*-
from os.path import exists as path_exists
from os.path import getmtime

import pytest

from pyscaffold import templates
from pyscaffold.api import (
    Extension,
    create_project,
    discover_actions,
    get_default_options,
    helpers,
    verify_project_dir,
)
from pyscaffold.exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
    InvalidIdentifier,
)


def create_extension(*hooks):
    """Shorthand to define extensions from a list of actions"""

    class TestExtension(Extension):
        def activate(self, actions):
            for hook in hooks:
                actions = self.register(actions, hook, after="define_structure")
            return actions

    return TestExtension("TestExtension")


def test_discover_actions():
    # Given an extension with actions,
    def fake_action(struct, opts):
        return struct, opts

    def extension(actions):
        return [fake_action] + actions

    # When discover_actions is called,
    actions = discover_actions([extension])

    # Then the extension actions should be listed alongside default actions.
    assert get_default_options in actions
    assert fake_action in actions


def test_create_project_call_extension_hooks(tmpfolder, git_mock):
    # Given an extension with hooks,
    called = []

    def pre_hook(struct, opts):
        called.append("pre_hook")
        return struct, opts

    def post_hook(struct, opts):
        called.append("post_hook")
        return struct, opts

    # when created project is called,
    create_project(project="proj", extensions=[create_extension(pre_hook, post_hook)])

    # then the hooks should also be called.
    assert "pre_hook" in called
    assert "post_hook" in called


def test_create_project_generate_extension_files(tmpfolder, git_mock):
    # Given a blank state,
    assert not path_exists("proj/tests/extra.file")
    assert not path_exists("proj/tests/another.file")

    # and an extension with extra files,
    def add_files(struct, opts):
        struct = helpers.ensure(struct, "proj/tests/extra.file", "content")
        struct = helpers.merge(struct, {"proj": {"tests": {"another.file": "content"}}})

        return struct, opts

    # when the created project is called,
    create_project(project="proj", extensions=[create_extension(add_files)])

    # then the files should be created
    assert path_exists("proj/tests/extra.file")
    assert tmpfolder.join("proj/tests/extra.file").read() == "content"
    assert path_exists("proj/tests/another.file")
    assert tmpfolder.join("proj/tests/another.file").read() == "content"


def test_create_project_respect_update_rules(tmpfolder, git_mock):
    # Given an existing project
    opts = dict(project="proj")
    create_project(opts)
    for i in (0, 1, 3, 5, 6):
        tmpfolder.ensure("proj/tests/file" + str(i)).write("old")
        assert path_exists("proj/tests/file" + str(i))

    # and an extension with extra files
    def add_files(struct, opts):
        nov, ncr = helpers.NO_OVERWRITE, helpers.NO_CREATE
        struct = helpers.ensure(struct, "proj/tests/file0", "new")
        struct = helpers.ensure(struct, "proj/tests/file1", "new", nov)
        struct = helpers.ensure(struct, "proj/tests/file2", "new", ncr)
        struct = helpers.merge(
            struct,
            {
                "proj": {
                    "tests": {
                        "file3": ("new", nov),
                        "file4": ("new", ncr),
                        "file5": ("new", None),
                        "file6": "new",
                    }
                }
            },
        )

        return struct, opts

    # When the created project is called,
    create_project(
        project="proj", update=True, extensions=[create_extension(add_files)]
    )

    # then the NO_CREATE files should not be created,
    assert not path_exists("proj/tests/file2")
    assert not path_exists("proj/tests/file4")
    # the NO_OVERWRITE files should not be updated
    assert tmpfolder.join("proj/tests/file1").read() == "old"
    assert tmpfolder.join("proj/tests/file3").read() == "old"
    # and files with no rules or `None` rules should be updated
    assert tmpfolder.join("proj/tests/file0").read() == "new"
    assert tmpfolder.join("proj/tests/file5").read() == "new"
    assert tmpfolder.join("proj/tests/file6").read() == "new"


def test_create_project_when_folder_exists(tmpfolder, git_mock):
    tmpfolder.ensure("my-project", dir=True)
    opts = dict(project="my-project")
    with pytest.raises(DirectoryAlreadyExists):
        create_project(opts)
    opts = dict(project="my-project", force=True)
    create_project(opts)


def test_create_project_with_valid_package_name(tmpfolder, git_mock):
    opts = dict(project="my-project", package="my_package")
    create_project(opts)


def test_create_project_with_invalid_package_name(tmpfolder, git_mock):
    opts = dict(project="my-project", package="my:package")
    with pytest.raises(InvalidIdentifier):
        create_project(opts)


def test_create_project_when_updating(tmpfolder, git_mock):
    opts = dict(project="my-project")
    create_project(opts)
    opts = dict(project="my-project", update=True)
    create_project(opts)
    assert path_exists("my-project")


def test_create_project_with_license(tmpfolder, git_mock):
    _, opts = get_default_options({}, dict(project="my-project", license="new-bsd"))
    # ^ The entire default options are needed, since template
    #   uses computed information

    create_project(opts)
    assert path_exists("my-project")
    content = tmpfolder.join("my-project/LICENSE.txt").read()
    assert content == templates.license(opts)


def test_get_default_opts():
    _, opts = get_default_options(
        {}, dict(project="project", package="package", description="description")
    )
    assert all(k in opts for k in "project update force author".split())
    assert isinstance(opts["extensions"], list)
    assert isinstance(opts["requirements"], list)


def test_get_default_opts_with_nogit(nogit_mock):
    with pytest.raises(GitNotInstalled):
        get_default_options({}, dict(project="my-project"))


def test_get_default_opts_with_git_not_configured(noconfgit_mock):
    with pytest.raises(GitNotConfigured):
        get_default_options({}, dict(project="my-project"))


def test_verify_project_dir_when_project_doesnt_exist_and_updating(tmpfolder, git_mock):
    with pytest.raises(DirectoryDoesNotExist):
        verify_project_dir({}, dict(project="my-project", update=True))


def test_verify_project_dir_when_project_exist_but_not_updating(tmpfolder, git_mock):
    tmpfolder.ensure("my-project", dir=True)
    with pytest.raises(DirectoryAlreadyExists):
        verify_project_dir({}, dict(project="my-project", update=False, force=False))


def test_api(tmpfolder):
    opts = dict(project="created_proj_with_api")
    create_project(opts)
    assert path_exists("created_proj_with_api")
    assert path_exists("created_proj_with_api/.git")


def test_pretend(tmpfolder):
    opts = dict(project="created_proj_with_api", pretend=True)
    create_project(opts)
    assert not path_exists("created_proj_with_api")


def test_pretend_when_updating_does_not_make_changes(tmpfolder):
    # Given a project already exists
    opts = dict(project="proj", license="mit")
    create_project(opts)

    setup_changed = getmtime("proj/setup.cfg")
    license_changed = getmtime("proj/LICENSE.txt")

    # When it is updated with different configuration,
    create_project(
        project="proj",
        update=True,
        force=True,
        pretend=True,
        url="my.project.net",
        license="mozilla",
    )

    # Then nothing should change
    assert getmtime("proj/setup.cfg") == setup_changed
    assert "my.project.net" not in tmpfolder.join("proj/setup.cfg").read()

    assert getmtime("proj/LICENSE.txt") == license_changed
    assert "MIT License" in tmpfolder.join("proj/LICENSE.txt").read()
