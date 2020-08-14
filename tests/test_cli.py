import logging
import os
import sys

import pytest

from pyscaffold import cli
from pyscaffold.exceptions import OldSetuptools
from pyscaffold.file_system import localize_path as lp

from .log_helpers import find_report


def test_parse_args():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts["project_path"] == "my-project"


def test_parse_verbose_option():
    for quiet in ("--verbose", "-v"):
        args = ["my-project", quiet]
        opts = cli.parse_args(args)
        assert opts["log_level"] == logging.INFO


def test_parse_default_log_level():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts["log_level"] == logging.WARNING


def test_parse_pretend():
    for flag in ["--pretend", "-P"]:
        opts = cli.parse_args(["my-project", flag])
        assert opts["pretend"]
    opts = cli.parse_args(["my-project"])
    assert not opts["pretend"]


def test_parse_list_actions():
    opts = cli.parse_args(["my-project", "--list-actions"])
    assert opts["command"] == cli.list_actions
    opts = cli.parse_args(["my-project"])
    assert opts["command"] == cli.run_scaffold


def test_parse_license_finds_best_fit():
    examples = {
        "apache": "Apache-2.0",
        "artistic": "Artistic-2.0",
        "affero": "AGPL-3.0-only",
        "eclipse": "EPL-1.0",
        "new-bsd": "BSD-3-Clause",
        "mozilla": "MPL-2.0",
        "gpl3": "GPL-3.0-only",
    }

    for key, value in examples.items():
        opts = cli.parse_args(["my-project", "--license", key])
        assert opts["license"] == value

    # option not passed
    assert "license" not in cli.parse_args(["my_project"])


def test_verbose_main(tmpfolder, git_mock, caplog):
    args = ["my-project", "--verbose"]
    cli.main(args)
    assert os.path.exists(args[0])

    # Check for some log messages
    assert find_report(caplog, "invoke", "get_default_options")
    assert find_report(caplog, "invoke", "verify_options_consistency")
    assert find_report(caplog, "invoke", "define_structure")
    assert find_report(caplog, "invoke", "create_structure")
    assert find_report(caplog, "create", "setup.py")
    assert find_report(caplog, "create", lp("my_project/__init__.py"))
    assert find_report(caplog, "run", "git init")
    assert find_report(caplog, "run", "git add")


def test_pretend_main(tmpfolder, git_mock, caplog):
    for flag in ["--pretend", "-P"]:
        args = ["my-project", flag]
        cli.main(args)
        assert not os.path.exists(args[0])

        # Check for some log messages
        assert find_report(caplog, "invoke", "get_default_options")
        assert find_report(caplog, "invoke", "verify_options_consistency")
        assert find_report(caplog, "invoke", "define_structure")
        assert find_report(caplog, "invoke", "create_structure")
        assert find_report(caplog, "create", "setup.py")
        assert find_report(caplog, "create", lp("my_project/__init__.py"))
        assert find_report(caplog, "run", "git init")
        assert find_report(caplog, "run", "git add")


def test_main_when_updating(tmpfolder, capsys, git_mock):
    args = ["my-project"]
    cli.main(args)
    args = ["--update", "my-project"]
    cli.main(args)
    assert os.path.exists(args[1])
    out, _ = capsys.readouterr()
    assert "Update accomplished!" in out


def test_main_with_old_setuptools(tmpfolder, old_setuptools_mock):
    args = ["my-project"]
    with pytest.raises(OldSetuptools):
        cli.main(args)


def test_main_with_list_actions(tmpfolder, capsys, isolated_logger):
    # When putup is called with --list-actions,
    args = ["my-project", "--no-tox", "--list-actions"]
    cli.main(args)
    # then the action list should be printed,
    out, _ = capsys.readouterr()
    assert "Planned Actions" in out
    assert "pyscaffold.actions:get_default_options" in out
    assert "pyscaffold.structure:define_structure" in out
    assert "pyscaffold.extensions.no_tox:remove_files" in out
    assert "pyscaffold.structure:create_structure" in out
    assert "pyscaffold.actions:init_git" in out
    # but no project should be created
    assert not os.path.exists(args[0])


def test_run(tmpfolder, git_mock):
    sys.argv = ["pyscaffold", "my-project"]
    cli.run()
    assert os.path.exists(sys.argv[1])
