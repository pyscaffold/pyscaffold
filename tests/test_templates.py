import sys
from configparser import ConfigParser
from pathlib import Path

import pytest

from pyscaffold import actions, api
from pyscaffold import dependencies as deps
from pyscaffold import info, templates


def test_get_template():
    template = templates.get_template("setup_py")
    content = template.safe_substitute()
    assert content.split("\n", 1)[0] == '"""'


@pytest.fixture
def tmp_python_path(tmp_path):
    sys.path.append(str(tmp_path))
    yield tmp_path
    sys.path.remove(str(tmp_path))


def test_get_template_relative_to(tmp_python_path):
    # Given a template exists inside a package
    parent = tmp_python_path / "pkg4test"
    pkg = tmp_python_path / "pkg4test" / "asdf42_123456"
    pkg.mkdir(parents=True, exist_ok=True)
    (parent / "__init__.py").touch(exist_ok=True)
    (parent / "ex1.template").write_text("${var1}")
    (pkg / "__init__.py").touch(exist_ok=True)
    (pkg / "ex2.template").write_text("${var2}")

    # When using "relative_to" with __name__
    import pkg4test

    tpl1 = templates.get_template("ex1", relative_to=pkg4test.__name__)
    content = tpl1.safe_substitute({"var1": "Hello World!"})
    # Then get_template should work
    assert content == "Hello World!"

    # When using "relative_to" with a module
    import pkg4test

    tpl1 = templates.get_template("ex1", relative_to=pkg4test)
    content = tpl1.safe_substitute({"var1": "Some World!"})
    # Then get_template should work
    assert content == "Some World!"

    # When using "relative_to" with a package name string
    tpl2 = templates.get_template("ex2", relative_to="pkg4test.asdf42_123456")
    content = tpl2.safe_substitute({"var2": "Bye bye World!"})
    # Then get_template should work
    assert content == "Bye bye World!"


def test_all_licenses():
    opts = {
        "email": "test@user",
        "name": "my_project",
        "author": "myself",
        "year": 1832,
    }
    for license in templates.licenses.keys():
        opts["license"] = license
        assert templates.license(opts)


def test_setup_cfg():
    reqs = ("mydep1>=789.8.1", "mydep3<=90009;python_version>'3.5'", "other")
    opts = api.bootstrap_options({"project_path": "myproj", "requirements": reqs})
    _, opts = actions.get_default_options({}, opts)
    text = templates.setup_cfg(opts)
    setup_cfg = ConfigParser()
    setup_cfg.read_string(text)

    # Assert install_requires is correctly assigned
    install_requires = deps.split(setup_cfg["options"]["install_requires"])
    for dep in reqs:
        assert dep in install_requires
    # Assert PyScaffold section
    assert setup_cfg["pyscaffold"].get("version")


def test_setup_cfg_2line_description(tmpfolder):
    # When a 2 line description is found (e.g. by reading an existing setup.cfg file)
    _, opts = actions.get_default_options({}, {"project_path": tmpfolder})
    opts["description"] = "2 line\ndescription"
    # Then the rendered template should still be valid
    text = templates.setup_cfg(opts)
    setup_cfg = ConfigParser()
    setup_cfg.read_string(text)
    assert setup_cfg["metadata"]["description"].strip() == "2 line\ndescription"

    Path(tmpfolder, "setup.cfg").write_text(text)
    opts = info.project({})
    assert opts["description"].strip() == "2 line\ndescription"
