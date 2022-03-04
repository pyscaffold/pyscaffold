import logging
import re
from pathlib import Path
from textwrap import dedent

from configupdater import ConfigUpdater

from pyscaffold import dependencies as deps
from pyscaffold import info
from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions.cirrus import Cirrus
from pyscaffold.extensions.cirrus import cirrus_descriptor as cirrus_template
from pyscaffold.extensions.namespace import Namespace
from pyscaffold.extensions.typed import (
    Typed,
    add_mypy_setupcfg,
    add_typecheck_cirrus,
    add_typecheck_tox,
    modify_file,
)
from pyscaffold.templates import get_template


class TestAddTypecheckCirrus:
    def test_removed_file(self):
        # When file is removed from structure, don't add a new one
        contents = add_typecheck_cirrus(None, {})
        assert contents is None

    def test_it_works_with_default_template(self):
        template = cirrus_template({})
        assert "typecheck_task:" in template
        assert "TYPE_CHECKING: false" in template
        contents = add_typecheck_cirrus(dedent(template), {})
        assert "TYPE_CHECKING: true" in contents


class TestAddTypecheckTox:
    def test_default_template(self):
        template = get_template("tox_ini").template
        assert "[testenv:typecheck]" in template

    def test_removed_file(self):
        # When file is removed from structure, don't add a new one
        contents = add_typecheck_tox(None, {})
        assert contents is None

    def test_already_existing_task(self):
        # When file exists and it contains the typecheck task, does not change it
        template = """\
        [testenv:typecheck]
        commands = pytest
        """
        contents = add_typecheck_tox(dedent(template), {})
        assert contents.count("[testenv:typecheck]") == 1
        assert "mypy" not in contents

    def test_no_existing_task(self):
        # When file exists without typecheck task, add it
        template = """\
        [testenv]
        commands = pytest
        """
        contents = add_typecheck_tox(dedent(template), {})
        assert "[testenv:typecheck]" in contents
        assert "mypy" in contents

    def test_deps(self):
        # Ensure ``typecheck_deps`` passed via opts are added to tox.ini
        opts = {
            "typecheck_deps": [
                "django-stubs",
                "mypy",
                "mypy>=0.910",  # let's check deduplication
            ]
        }
        template = """\
        [testenv]
        commands = pytest
        """
        contents = add_typecheck_tox(dedent(template), opts)
        toxini = ConfigUpdater().read_string(contents)
        dependencies = deps.split(toxini["testenv:typecheck"]["deps"].value)
        assert list(sorted(dependencies)) == ["django-stubs", "mypy>=0.910"]


class TestAddMypyConfig:
    def test_default_template(self):
        template = get_template("setup_cfg").template
        assert "[mypy]" in template

    def test_removed_file(self):
        # When file is removed from structure, don't add a new one
        contents = add_mypy_setupcfg(None, {})
        assert contents is None

    def test_already_existing_task(self):
        # When file exists and it contains the mypy config, does not change it
        template = """\
        [metadata]
        name = project

        [mypy]
        ignore_missing_imports = False
        """
        contents = add_mypy_setupcfg(dedent(template), {})
        assert contents.count("[mypy]") == 1
        assert "ignore_missing_imports = False" in contents
        assert "show_error_context" not in contents

    def test_no_existing_task(self):
        # When file exists without mypy config, add it
        template = """\
        [metadata]
        name = project
        """
        contents = add_mypy_setupcfg(dedent(template), {})
        assert "[mypy]" in contents
        assert "ignore_missing_imports = True" in contents
        assert "show_error_context" in contents

    def test_plugins(self):
        # Ensure ``mypy_plugins`` passed via opts are added to mypy config
        opts = {
            "mypy_plugins": [
                "mypy_django_plugin.main",
                "mypy_django_plugin.main",  # let's check deduplication
                "returns.contrib.mypy.returns_plugin",
            ]
        }
        template = """\
        [testenv]
        commands = pytest
        """
        contents = add_mypy_setupcfg(dedent(template), opts)
        setupcfg = ConfigUpdater().read_string(contents)
        dependencies = setupcfg["mypy"]["plugins"].value
        expected = "mypy_django_plugin.main, returns.contrib.mypy.returns_plugin"
        assert dependencies == expected


class TestModifyFile:
    def test_pretend(self, tmpfolder, caplog):
        caplog.set_level(logging.DEBUG)

        # When the pretend option is passed
        opts = {"project_path": Path("."), "pretend": True}
        existing = """\
        [testenv]
        commands = pytest
        """
        (tmpfolder / "tox.ini").write_text(dedent(existing), "utf-8")
        modify_file("tox.ini", add_typecheck_tox, opts)

        # Then the files are not changed
        result = (tmpfolder / "tox.ini").read_text("utf-8")
        assert result == dedent(existing)
        assert "[testenv:typecheck]" not in result

        # But the action is logged
        logs = re.sub(r"\s+", " ", caplog.text)  # normalise whitespace
        assert "updated tox.ini" in logs

    def test_no_pretend(self, tmpfolder):
        opts = {"project_path": Path(".")}
        existing = """\
        [testenv]
        commands = pytest
        """
        (tmpfolder / "tox.ini").write_text(dedent(existing), "utf-8")
        modify_file("tox.ini", add_typecheck_tox, opts)

        result = (tmpfolder / "tox.ini").read_text("utf-8")
        assert result != dedent(existing)
        assert dedent(existing) in result
        assert "[testenv:typecheck]" in result

    def test_no_file(self, tmpfolder):
        opts = {"project_path": Path(".")}
        assert modify_file("tox.ini", add_typecheck_tox, opts) is None
        assert not (tmpfolder / "tox.ini").exists()


class TestTyped:
    def test_create_project_without_typed(self, tmpfolder):
        # Given options without the typed extension,
        opts = dict(project_path="proj", extensions=[Cirrus()])

        # when the project is created,
        struct, opts = create_project(opts)

        # then files from typed extension should not exist
        assert not Path("proj/src/proj/py.typed").exists()

        # the changes in other files do not take place,
        cirrusyml = Path("proj/.cirrus.yml").read_text()
        assert "TYPE_CHECKING: false" in cirrusyml

        # and the `typed` option should be False
        assert opts.get("typed", False) is False

    def test_create_project(self, tmpfolder):
        # Given options with the typed extension,
        opts = dict(project_path="proj", extensions=[Typed()])

        # when the project is created,
        struct, opts = create_project(opts)

        # then files from typed extension should exist
        assert Path("proj/src/proj/py.typed").exists()

        # and the `typed` option should be set to indicate to other extensions
        assert opts["typed"] is True

        # Without the cirrus extension, the .cirrus.yml should not exist
        assert not Path("proj/.cirrus.yml").exists()

    def test_create_project_with_cirrus(self, tmpfolder):
        # Given options with the typed extension,
        opts = dict(project_path="proj", extensions=[Typed(), Cirrus()])

        # when the project is created,
        create_project(opts)

        # then .cirrus.yml should exist and typechecking should be activated
        assert Path("proj/.cirrus.yml").exists()
        cirrusyml = Path("proj/.cirrus.yml").read_text()
        assert "TYPE_CHECKING: true" in cirrusyml

    def test_create_project_with_namespace(self, tmpfolder):
        # Given options with the typed and namespace extensions,
        opts = dict(
            project_path="proj",
            namespace="ns.nested_ns",
            extensions=[Typed(), Namespace()],
        )

        # when the project is created,
        create_project(opts)

        # then the `py.typed` file should be in the right place
        assert not Path("proj/src/proj/py.typed").exists()
        assert Path("proj/src/ns/nested_ns/proj/py.typed").exists()

        # and the tox task should be configure to run mypy in the right directory
        toxini = Path("proj/tox.ini").read_text()
        assert "mypy {posargs:src/ns/nested_ns}" in toxini

    def test_update_project(self, tmpfolder, monkeypatch):
        # Given a project created without typed and lacking proper configs
        self.test_create_project_without_typed(tmpfolder)
        setupcfg = ConfigUpdater().read("proj/setup.cfg")
        setupcfg.pop("mypy", None)
        setupcfg.update_file()
        assert "mypy" not in setupcfg
        toxini = ConfigUpdater().read("proj/tox.ini")
        toxini.pop("testenv:typecheck", None)
        toxini.update_file()
        assert "testenv:typecheck" not in toxini
        monkeypatch.setattr(info, "is_git_workspace_clean", lambda *_: True)

        # When the same project is updated with typed
        opts = dict(project_path="proj", update=True, extensions=[Typed(), Cirrus()])
        create_project(opts)

        # then the config files are updated
        setupcfg = Path("proj/setup.cfg").read_text()
        assert "ignore_missing_imports" in setupcfg
        toxini = Path("proj/tox.ini").read_text()
        assert "testenv:typecheck" in toxini
        cirrusyml = Path("proj/.cirrus.yml").read_text()
        assert "TYPE_CHECKING: true" in cirrusyml


class TestCli:
    def test_with_typed(self, tmpfolder):
        # Given the command line with the typed option
        args = ["--typed", "--cirrus", "proj"]

        # when pyscaffold runs,
        run(args)

        # then typing support config should exist
        assert Path("proj/src/proj/py.typed").exists()
        setupcfg = Path("proj/setup.cfg").read_text()
        assert "ignore_missing_imports" in setupcfg
        toxini = Path("proj/tox.ini").read_text()
        assert "testenv:typecheck" in toxini
        cirrusyml = Path("proj/.cirrus.yml").read_text()
        assert "TYPE_CHECKING: true" in cirrusyml

    def test_with_typed_and_pretend(self, tmpfolder):
        # Given the command line with the cirrus and pretend options
        args = ["--pretend", "--typed", "--cirrus", "proj"]

        # when pyscaffold runs,
        run(args)

        # then typing support files should not exist
        assert not Path("proj/src/proj/py.typed").exists()
        # (or the project itself)
        assert not Path("proj").exists()

    def test_without_typed(self, tmpfolder):
        # Given the command line without the typed option,
        args = ["proj"]

        # when pyscaffold runs,
        run(args)

        # then created files should not exist
        assert not Path("proj/src/proj/py.typed").exists()
