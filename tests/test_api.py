from os.path import getmtime
from pathlib import Path
from textwrap import dedent

import pytest

from pyscaffold import cli, info, operations, structure, templates
from pyscaffold.actions import get_default_options
from pyscaffold.api import NO_CONFIG, bootstrap_options, create_project
from pyscaffold.exceptions import (
    DirectoryAlreadyExists,
    InvalidIdentifier,
    NoPyScaffoldProject,
)
from pyscaffold.extensions import Extension
from pyscaffold.file_system import chdir


def create_extension(*hooks):
    """Shorthand to define extensions from a list of actions"""

    class TestExtension(Extension):
        def activate(self, actions):
            for hook in hooks:
                actions = self.register(actions, hook, after="define_structure")
            return actions

    return TestExtension()


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
        struct = structure.ensure(struct, "tests/extra.file", "content")
        struct = structure.merge(struct, {"tests": {"another.file": "content"}})

        return struct, opts

    # when the created project is called,
    create_project(project_path="proj", extensions=[create_extension(add_files)])

    # then the files should be created
    assert Path("proj/tests/extra.file").exists()
    assert tmpfolder.join("proj/tests/extra.file").read() == "content"
    assert Path("proj/tests/another.file").exists()
    assert tmpfolder.join("proj/tests/another.file").read() == "content"


def test_create_project_respect_operations(tmpfolder, git_mock):
    # Given an existing project
    create_project(project_path="proj")
    for i in (0, 1, 3, 5, 6):
        tmpfolder.ensure("proj/tests/file" + str(i)).write("old")
        assert Path("proj/tests/file" + str(i)).exists()

    # and an extension with extra files
    def add_files(struct, opts):
        nov, sou = operations.no_overwrite(), operations.skip_on_update()
        struct = structure.ensure(struct, "tests/file0", "new")
        struct = structure.ensure(struct, "tests/file1", "new", nov)
        struct = structure.ensure(struct, "tests/file2", "new", sou)
        struct = structure.merge(
            struct,
            {
                "tests": {
                    "file3": ("new", nov),
                    "file4": ("new", sou),
                    "file5": ("new", operations.create),
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
        {}, dict(project_path="my-project", license="BSD-3-Clause")
    )
    # ^ The entire default options are needed, since template
    #   uses computed information

    create_project(opts)
    assert Path("my-project").exists()
    content = tmpfolder.join("my-project/LICENSE.txt").read()
    assert content == templates.license(opts)


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
    opts = dict(project_path="proj", license="MIT")
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
        license="MPL-2.0",
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
    # First we create a config file
    opts = dict(project_path="proj", name="my-proj", license="MPL-2.0")
    opts = bootstrap_options(opts)
    _, opts = get_default_options({}, opts)
    setup_cfg = Path(str(tmpfolder.join("setup.cfg")))
    setup_cfg.write_text(templates.setup_cfg(opts))

    # Then we input this configfile to the API
    new_opts = dict(project_path="another", config_files=[str(setup_cfg)])
    new_opts = bootstrap_options(new_opts)

    # Finally, the bootstraped options should contain the same values
    # as the given config file
    assert new_opts["name"] == "my-proj"
    assert new_opts["package"] == "my_proj"
    assert new_opts["license"] == "MPL-2.0"
    assert str(new_opts["project_path"]) == "another"
    assert all(k in new_opts for k in "author email url".split())


@pytest.fixture
def with_default_config(fake_config_dir):
    config = dedent(
        """\
        [metadata]
        author = John Doe
        author-email = john.joe@gmail.com

        [pyscaffold]
        extensions =
            namespace
            cirrus
        namespace = my_namespace.my_sub_namespace
        """
    )
    cfg = fake_config_dir / info.CONFIG_FILE
    cfg.write_text(config)

    yield cfg


def test_bootstrap_with_default_config(tmpfolder, with_default_config):
    # Given a default config file exists and contains stuff
    _ = with_default_config
    # when bootstrapping options
    opts = dict(project_path="xoxo")
    new_opts = bootstrap_options(opts)
    # the stuff will be considered
    assert new_opts["author"] == "John Doe"
    assert new_opts["email"] == "john.joe@gmail.com"
    assert new_opts["namespace"] == "my_namespace.my_sub_namespace"
    extensions = new_opts["extensions"]
    assert len(extensions) == 2
    extensions_names = sorted([e.name for e in extensions])
    assert " ".join(extensions_names) == "cirrus namespace"


def test_bootstrap_with_no_config(tmpfolder, with_default_config):
    # Given a default config file exists and contains stuff
    _ = with_default_config
    # when bootstrapping options with NO_CONFIG
    opts = dict(project_path="xoxo", config_files=NO_CONFIG)
    new_opts = bootstrap_options(opts)
    # the stuff will not be considered
    assert new_opts.get("author") != "John Doe"
    assert new_opts.get("email") != "john.joe@gmail.com"
    assert new_opts.get("namespace") != "my_namespace.my_sub_namespace"
    extensions = new_opts.get("extensions", [])
    assert len(extensions) != 2
    extensions_names = sorted([e.name for e in extensions])
    assert " ".join(extensions_names) != "cirrus namespace"


def test_create_project_with_default_config(tmpfolder, with_default_config):
    # Given a default config file exists and contains stuff
    _ = with_default_config
    project = Path(str(tmpfolder)) / "xoxo"
    # when a new project is created
    create_project(project_path="xoxo", name="project")
    # then the default config is considered
    assert (project / "src/my_namespace/my_sub_namespace/project").exists()
    assert (project / "tox.ini").exists()
    assert (project / ".cirrus.yml").exists()


@pytest.fixture
def with_existing_proj_config(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "setup.cfg").write_text(
        dedent(
            """\
            [metadata]
            name = SuperProj
            description = some text
            author = John Doe
            author-email = john.doe@example.com
            url = www.example.com
            license = gpl3

            [pyscaffold]
            package = super_proj
            """
        )
    )
    with chdir(str(proj)):
        yield proj


def test_options_with_existing_proj_config_and_cli(with_existing_proj_config):
    # Given an existing project with a setup.cfg
    _ = with_existing_proj_config
    # When the CLI is called with no extra parameters
    opts = cli.parse_args(["--update", "."])
    opts = bootstrap_options(opts)
    _, opts = get_default_options({}, opts)

    # After all the opt processing actions are finished
    # The parameters in the old setup.py files are preserved
    assert opts["name"] == "SuperProj"
    assert opts["description"] == "some text"
    assert opts["author"] == "John Doe"
    assert opts["email"] == "john.doe@example.com"
    assert opts["url"] == "www.example.com"
    assert opts["license"] == "GPL-3.0-only"
    assert opts["package"] == "super_proj"
