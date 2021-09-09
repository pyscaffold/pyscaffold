from pathlib import Path
from textwrap import dedent

from configupdater import ConfigUpdater
from pyscaffold import dependencies as deps
from pyscaffold.extensions.typed import (
    add_mypy_config,
    add_typecheck_cirrus,
    add_typecheck_tox,
)


class TestAddTypecheckCirrus:
    def test_no_existing_template(self):
        # When file does not exist previously, don't add a new one
        contents = add_typecheck_cirrus(None, {})
        assert contents is None

    def test_already_existing_task(self):
        # When file exists and it contains the typecheck task, does not change it
        template = """\
        env:
          PATH: ${HOME}/.local/bin:${PATH}

        typecheck_task:
          <<: *OTHER_TEMPLATE
        """
        contents = add_typecheck_cirrus(dedent(template), {})
        assert contents.count("typecheck_task:") == 1
        assert "typecheck_script:" not in contents

    def test_no_existing_task(self):
        # When configuration exists without typecheck task, add it
        template = """\
        env:
          PATH: ${HOME}/.local/bin:${PATH}
        """
        contents = add_typecheck_cirrus(dedent(template), {})
        assert "typecheck_task:" in contents
        assert "typecheck_script:" in contents


class TestAddTypecheckTox:
    def test_no_existing_template(self):
        # When file does not exist previously, don't add a new one
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
    def test_no_existing_template(self):
        # When file does not exist previously, don't add a new one
        contents = add_mypy_config(None, {})
        assert contents is None

    def test_already_existing_task(self):
        # When file exists and it contains the mypy config, does not change it
        template = """\
        [metadata]
        name = project

        [mypy]
        ignore_missing_imports = False
        """
        contents = add_mypy_config(dedent(template), {})
        assert contents.count("[mypy]") == 1
        assert "ignore_missing_imports = False" in contents
        assert "show_error_context" not in contents

    def test_no_existing_task(self):
        # When file exists without mypy config, add it
        template = """\
        [metadata]
        name = project
        """
        contents = add_mypy_config(dedent(template), {})
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
        contents = add_mypy_config(dedent(template), opts)
        setupcfg = ConfigUpdater().read_string(contents)
        dependencies = setupcfg["mypy"]["plugins"].value
        expected = "mypy_django_plugin.main, returns.contrib.mypy.returns_plugin"
        assert dependencies == expected
