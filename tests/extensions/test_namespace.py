#!/usr/bin/env python
import sys
from pathlib import Path

import pytest

from pyscaffold.actions import get_default_options
from pyscaffold.api import create_project
from pyscaffold.cli import parse_args, run
from pyscaffold.exceptions import InvalidIdentifier
from pyscaffold.extensions.namespace import (
    Namespace,
    add_namespace,
    enforce_namespace_options,
    move_old_package,
    prepare_namespace,
)
from pyscaffold.log import logger


def test_prepare_namespace():
    namespaces = prepare_namespace("com")
    assert namespaces == ["com"]
    namespaces = prepare_namespace("com.blue_yonder")
    assert namespaces == ["com", "com.blue_yonder"]
    with pytest.raises(InvalidIdentifier):
        prepare_namespace("com.blue-yonder")


def test_add_namespace(isolated_logger, caplog):
    args = ["project", "-p", "package", "--namespace", "com.blue_yonder"]
    opts = parse_args(args)
    opts["ns_list"] = prepare_namespace(opts["namespace"])
    struct = {"src": {"package": {"file1": "Content"}}}

    ns_struct, _ = add_namespace(struct, opts)

    ns_pkg_struct = ns_struct["src"]
    assert "project" not in set(ns_pkg_struct.keys())
    assert "package" not in set(ns_pkg_struct.keys())
    assert {"com"} == set(ns_pkg_struct.keys())
    modules = set(ns_pkg_struct["com"].keys())
    assert {"blue_yonder", "__init__.py"} == modules
    submodules = set(ns_pkg_struct["com"]["blue_yonder"].keys())
    assert "package" in submodules

    # warnings should not be logged
    log = caplog.text
    unexpected_log = ("empty namespace", "valid string", "the `--namespace` option")
    for text in unexpected_log:
        assert text not in log


def test_add_namespace_empty(isolated_logger, caplog):
    # When trying to add a namespace without actually providing a namespace string
    add_namespace({}, {})

    # then something should be logged,
    log = caplog.text
    expected_log = ("empty namespace", "valid string", "the `--namespace` option")
    for text in expected_log:
        assert text in log


def test_create_project_with_namespace(tmpfolder):
    # Given options with the namespace extension,
    opts = dict(project_path="my-proj", namespace="ns.ns2", extensions=[Namespace()])

    # when the project is created,
    create_project(opts)

    # then namespace __init__ should not exist
    assert not Path("my-proj/src/ns/__init__.py").exists()
    assert not Path("my-proj/src/ns/ns2/__init__.py").exists()
    # but the package __init__ should
    assert Path("my-proj/src/ns/ns2/my_proj/__init__.py").exists()
    # and plain structure should not exist
    assert not Path("my-proj/src/my_proj/__init__.py").exists()


def test_create_project_with_empty_namespace(tmpfolder):
    for j, ns in enumerate(["", None, False]):
        # Given options with the namespace extension,
        opts = dict(project_path=f"my-proj{j}", namespace=ns, extensions=[Namespace()])

        # when the project is created,
        create_project(opts)

        # then plain structure should exist
        path = Path(f"my-proj{j}/src/my_proj{j}/__init__.py")
        assert path.exists()


def test_create_project_without_namespace(tmpfolder):
    # Given options without the namespace extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then plain structure should exist
    assert Path("proj/src/proj/__init__.py").exists()


def test_cli_with_namespace(tmpfolder):
    # Given the command line with the namespace option,
    sys.argv = ["pyscaffold", "proj", "--namespace", "ns"]

    # when pyscaffold runs,
    run()

    # then namespace __init__ package should not exist
    assert not Path("proj/src/ns/__init__.py").exists()
    # but the package's should
    assert Path("proj/src/ns/proj/__init__.py").exists()


def test_cli_with_namespace_and_pretend(tmpfolder):
    # Given the command line with the namespace and pretend options
    sys.argv = ["pyscaffold", "proj", "--namespace", "ns", "--pretend"]

    # when pyscaffold runs,
    run()

    # then namespace __init__ package should not exist (or even the project)
    assert not Path("proj/src/ns/__init__.py").exists()
    assert not Path("proj").exists()


def test_cli_with_empty_namespace(tmpfolder, capsys):
    # Given the command line with the namespace option,
    sys.argv = ["pyscaffold", "proj", "--namespace"]

    # when pyscaffold runs,
    with pytest.raises(SystemExit):
        run()

    # then an error occurs
    _, err = capsys.readouterr()
    assert "expected one argument" in err


def test_cli_without_namespace(tmpfolder):
    # Given the command line without the namespace option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then namespace dir should not exist
    assert not Path("proj/src/ns").exists()


def test_move_old_package_without_namespace(tmpfolder):
    # Given a package is already created without namespace
    create_project(project_path="proj", package="my_pkg")

    opts = dict(project_path="proj", package="my_pkg")
    struct = {"src": {"my_pkg": {"file.py": ""}}}

    # when no 'namespace' option is passed,
    struct, opts = get_default_options(struct, opts)
    struct, opts = enforce_namespace_options(struct, opts)
    struct, opts = move_old_package(struct, opts)

    # then the old package remains,
    assert tmpfolder.join("proj/src/my_pkg/__init__.py").check()


def test_move_old_package(tmpfolder):
    # Given a package is already created without namespace
    create_project(project_path="proj", package="my_pkg")
    assert tmpfolder.join("proj/src/my_pkg/__init__.py").check()

    opts = dict(project_path="proj", package="my_pkg", namespace="my.ns")
    struct = {"src": {"my_pkg": {"file.py": ""}}}

    # when the 'namespace' option is passed,
    struct, opts = get_default_options(struct, opts)
    struct, opts = enforce_namespace_options(struct, opts)
    struct, opts = move_old_package(struct, opts)

    # then the old package should be moved
    assert not tmpfolder.join("proj/src/my_pkg/__init__.py").check()
    assert tmpfolder.join("proj/src/my/ns/my_pkg/__init__.py").check()


def test_pretend_move_old_package(tmpfolder, caplog, isolated_logger):
    # Given a package is already created without namespace
    create_project(project_path="proj", package="my_pkg")

    opts = parse_args(["proj", "-p", "my_pkg", "--namespace", "my.ns", "--pretend"])
    struct = {"src": {"my_pkg": {"file.py": ""}}}
    logger.reconfigure(opts)

    # when 'pretend' option is passed,
    struct, opts = get_default_options(struct, opts)
    struct, opts = enforce_namespace_options(struct, opts)
    struct, opts = move_old_package(struct, opts)

    # then nothing should happen,
    assert tmpfolder.join("proj/src/my_pkg/__init__.py").check()
    assert not tmpfolder.join("proj/src/my/ns").check()

    # something should be logged,
    log = caplog.text
    expected_log = ("move", "my_pkg", "to", str(Path("my/ns")))
    for text in expected_log:
        assert text in log

    # but user should see no warning,
    unexpected_warnings = (
        "A folder",
        "exists in the project directory",
        "a namespace option was passed",
        "Please make sure",
    )
    for text in unexpected_warnings:
        assert text not in log


def test_updating_existing_project(tmpfolder, caplog):
    # Given a project already exists, but was generated without
    # namespace,
    create_project(project_path="my-proj")
    assert tmpfolder.join("my-proj/src/my_proj").check()
    assert not tmpfolder.join("my-proj/src/my/ns").check()

    # when the project is updated with a namespace,
    create_project(
        project_path="my-proj", update=True, namespace="my.ns", extensions=[Namespace()]
    )

    # then the package folder should be moved to a nested position,
    assert not tmpfolder.join("my-proj/src/my_proj").check()
    assert tmpfolder.join("my-proj/src/my/ns/my_proj").check()

    # and the user should see a warn
    expected_warnings = (
        "A folder",
        "exists in the project directory",
        "a namespace option was passed",
        "Please make sure",
    )
    log = caplog.text
    for text in expected_warnings:
        assert text in log
