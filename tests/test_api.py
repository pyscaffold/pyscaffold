# -*- coding: utf-8 -*-
from os.path import getmtime
from pathlib import Path

import pytest

from pyscaffold import info, templates
from pyscaffold.api import (
    Extension,
    bootstrap_options,
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
    NoPyScaffoldProject,
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
    create_project(
        project_path="proj", extensions=[create_extension(pre_hook, post_hook)]
    )

    # then the hooks should also be called.
    assert "pre_hook" in called
    assert "post_hook" in called


def test_create_project_generate_extension_files(tmpfolder, git_mock):
    # Given a blank state,
    assert not Path("proj/tests/extra.file").exists()
    assert not Path("proj/tests/another.file").exists()

    # and an extension with extra files,
    def add_files(struct, opts):
        struct = helpers.ensure(struct, "tests/extra.file", "content")
        struct = helpers.merge(struct, {"tests": {"another.file": "content"}})

        return struct, opts

    # when the created project is called,
    create_project(project_path="proj", extensions=[create_extension(add_files)])

    # then the files should be created
    assert Path("proj/tests/extra.file").exists()
    assert tmpfolder.join("proj/tests/extra.file").read() == "content"
    assert Path("proj/tests/another.file").exists()
    assert tmpfolder.join("proj/tests/another.file").read() == "content"


def test_create_project_respect_update_rules(tmpfolder, git_mock):
    # Given an existing project
    create_project(project_path="proj")
    for i in (0, 1, 3, 5, 6):
        tmpfolder.ensure("proj/tests/file" + str(i)).write("old")
        assert Path("proj/tests/file" + str(i)).exists()

    # and an extension with extra files
    def add_files(struct, opts):
        nov, ncr = helpers.NO_OVERWRITE, helpers.NO_CREATE
        struct = helpers.ensure(struct, "tests/file0", "new")
        struct = helpers.ensure(struct, "tests/file1", "new", nov)
        struct = helpers.ensure(struct, "tests/file2", "new", ncr)
        struct = helpers.merge(
            struct,
            {
                "tests": {
                    "file3": ("new", nov),
                    "file4": ("new", ncr),
                    "file5": ("new", None),
                    "file6": "new",
                }
            },
        )

        return struct, opts

    # When the created project is called,
    create_project(
        project_path="proj", update=True, extensions=[create_extension(add_files)]
    )

    # then the NO_CREATE files should not be created,
    assert not Path("proj/tests/file2").exists()
    assert not Path("proj/tests/file4").exists()
    # the NO_OVERWRITE files should not be updated
    assert tmpfolder.join("proj/tests/file1").read() == "old"
    assert tmpfolder.join("proj/tests/file3").read() == "old"
    # and files with no rules or `None` rules should be updated
    assert tmpfolder.join("proj/tests/file0").read() == "new"
    assert tmpfolder.join("proj/tests/file5").read() == "new"
    assert tmpfolder.join("proj/tests/file6").read() == "new"


def test_create_project_when_folder_exists(tmpfolder, git_mock):
    tmpfolder.ensure("my-project", dir=True)
    opts = dict(project_path="my-project")
    with pytest.raises(DirectoryAlreadyExists):
        create_project(opts)
    opts = dict(project_path="my-project", force=True)
    create_project(opts)


def test_create_project_with_valid_package_name(tmpfolder, git_mock):
    opts = dict(project_path="my-project", package="my_package")
    create_project(opts)


def test_create_project_with_invalid_package_name(tmpfolder, git_mock):
    opts = dict(project_path="my-project", package="my:package")
    with pytest.raises(InvalidIdentifier):
        create_project(opts)


def test_create_project_when_updating(tmpfolder, git_mock):
    opts = dict(project_path="my-project")
    create_project(opts)
    opts = dict(project_path="my-project", update=True)
    create_project(opts)
    assert Path("my-project").exists()


def test_create_project_with_license(tmpfolder, git_mock):
    _, opts = get_default_options(
        {}, dict(project_path="my-project", license="new-bsd")
    )
    # ^ The entire default options are needed, since template
    #   uses computed information

    create_project(opts)
    assert Path("my-project").exists()
    content = tmpfolder.join("my-project/LICENSE.txt").read()
    assert content == templates.license(opts)


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


def test_api(tmpfolder):
    opts = dict(project_path="created_proj_with_api")
    create_project(opts)
    assert Path("created_proj_with_api").exists()
    assert Path("created_proj_with_api/.git").exists()


def test_pretend(tmpfolder):
    opts = dict(project_path="created_proj_with_api", pretend=True)
    create_project(opts)
    assert not Path("created_proj_with_api").exists()


def test_pretend_when_updating_does_not_make_changes(tmpfolder):
    # Given a project already exists
    opts = dict(project_path="proj", license="mit")
    create_project(opts)

    setup_changed = getmtime("proj/setup.cfg")
    license_changed = getmtime("proj/LICENSE.txt")

    # When it is updated with different configuration,
    create_project(
        project_path="proj",
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


def test_bootstrap_opts_raises_when_updating_non_existing():
    with pytest.raises(NoPyScaffoldProject):
        bootstrap_options(project_path="non-existent", update=True)


def test_bootstrap_opts_raises_when_config_file_doesnt_exist():
    opts = dict(project_path="non-existent", config_files=["non-existent.cfg"])
    with pytest.raises(FileNotFoundError):
        bootstrap_options(opts)


def test_bootstrap_using_config_file(tmpfolder):
    # First we create a project just for the sake of producing a config file
    opts = dict(project_path="proj", name="my-proj")
    create_project(opts)
    # Then we input this configfile to the API
    setup_cfg = tmpfolder.join("proj", "setup.cfg")
    new_opts = dict(project_path="another", config_files=[str(setup_cfg)])
    new_opts = bootstrap_options(new_opts)
    # Finally, the bootstraped options should contain the same values
    # as the given config file
    assert new_opts["name"] == "my-proj"
    assert new_opts["package"] == "my_proj"
    assert str(new_opts["project_path"]) == "another"
    assert all(k in new_opts for k in "author email license url".split())


@pytest.fixture
def with_default_config(fake_config_dir):
    config = """\
    [metadata]
    name = project
    author = John Doe
    author-email = john.joe@gmail.com

    [pyscaffold]
    extensions =
        namespace
        tox
        travis
    namespace = my_namespace.my_sub_namespace
    """
    cfg = fake_config_dir / info.DEFAULT_CONFIG_FILE
    cfg.write_text(config)

    yield cfg


def test_bootstrap_with_default_config(tmpfolder, with_default_config):
    # Given a default config file exists and contains stuff
    _ = with_default_config
    # when bootstrapping options
    opts = dict(project_path="xoxo", url="")
    new_opts = bootstrap_options(opts)
    # the stuff will be considered
    assert new_opts["name"] == "project"
    assert new_opts["author"] == "John Doe"
    assert new_opts["email"] == "john.joe@gmail.com"
    assert new_opts["namespace"] == "my_namespace.my_sub_namespace"
    extensions = new_opts["extensions"]
    assert len(extensions) == 3
    extensions_names = sorted([e.name for e in extensions])
    assert " ".join(extensions_names) == "namespace tox travis"


def test_create_project_with_default_config(tmpfolder, with_default_config):
    # Given a default config file exists and contains stuff
    _ = with_default_config
    project = Path(str(tmpfolder)) / "xoxo"
    # when a new project is created
    create_project(project_path="xoxo")
    # then the default config is considered
    assert (project / "src/my_namespace/my_sub_namespace/project").exists()
    assert (project / "tox.ini").exists()
    assert (project / ".travis.yml").exists()
