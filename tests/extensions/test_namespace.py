#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists
from pathlib import Path

import pytest

from pyscaffold.api import create_project, get_default_options
from pyscaffold.cli import parse_args, process_opts, run
from pyscaffold.extensions import namespace
from pyscaffold.extensions.namespace import (
    add_namespace,
    enforce_namespace_options,
    move_old_package,
)
from pyscaffold.log import logger
from pyscaffold.utils import prepare_namespace


def test_add_namespace():
    args = ["project", "-p", "package", "--namespace", "com.blue_yonder"]
    opts = parse_args(args)
    opts = process_opts(opts)
    opts["ns_list"] = prepare_namespace(opts["namespace"])
    struct = {"project": {"src": {"package": {"file1": "Content"}}}}
    ns_struct, _ = add_namespace(struct, opts)
    ns_pkg_struct = ns_struct["project"]["src"]
    assert ["project"] == list(ns_struct.keys())
    assert "package" not in list(ns_struct.keys())
    assert ["com"] == list(ns_pkg_struct.keys())
    assert {"blue_yonder", "__init__.py"} == set(ns_pkg_struct["com"].keys())
    assert "package" in list(ns_pkg_struct["com"]["blue_yonder"].keys())


def test_create_project_with_namespace(tmpfolder):
    # Given options with the namespace extension,
    opts = dict(
        project="my-proj",
        namespace="ns.ns2",
        extensions=[namespace.Namespace("namespace")],
    )

    # when the project is created,
    create_project(opts)

    # then nested structure should exist
    assert path_exists("my-proj/src/ns/__init__.py")
    assert path_exists("my-proj/src/ns/ns2/__init__.py")
    assert path_exists("my-proj/src/ns/ns2/my_proj/__init__.py")
    # and plain structure should not exist
    assert not path_exists("my-proj/src/my_proj/__init__.py")


def test_create_project_with_empty_namespace(tmpfolder):
    for j, ns in enumerate(["", None, False]):
        # Given options with the namespace extension,
        opts = dict(
            project="my-proj{}".format(j),
            namespace=ns,
            extensions=[namespace.Namespace("namespace")],
        )

        # when the project is created,
        create_project(opts)

        # then plain structure should exist
        assert path_exists("my-proj{}/src/my_proj{}/__init__.py".format(j, j))


def test_create_project_without_namespace(tmpfolder):
    # Given options without the namespace extension,
    opts = dict(project="proj")

    # when the project is created,
    create_project(opts)

    # then plain structure should exist
    assert path_exists("proj/src/proj/__init__.py")


def test_cli_with_namespace(tmpfolder):
    # Given the command line with the namespace option,
    sys.argv = ["pyscaffold", "proj", "--namespace", "ns"]

    # when pyscaffold runs,
    run()

    # then namespace package should exist
    assert path_exists("proj/src/ns/__init__.py")
    assert path_exists("proj/src/ns/proj/__init__.py")


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

    # then namespace files should not exist
    assert not path_exists("proj/src/ns/__init__.py")


def test_move_old_package_without_namespace(tmpfolder):
    # Given a package is already created without namespace
    create_project(project="proj", package="my_pkg")

    opts = dict(project="proj", package="my_pkg")
    struct = dict(proj={"src": {"my_pkg": {"file.py": ""}}})

    # when no 'namespace' option is passed,
    struct, opts = get_default_options(struct, opts)
    struct, opts = enforce_namespace_options(struct, opts)
    struct, opts = move_old_package(struct, opts)

    # then the old package remains,
    assert tmpfolder.join("proj/src/my_pkg/__init__.py").check()


def test_move_old_package(tmpfolder):
    # Given a package is already created without namespace
    create_project(project="proj", package="my_pkg")
    assert tmpfolder.join("proj/src/my_pkg/__init__.py").check()

    opts = dict(project="proj", package="my_pkg", namespace="my.ns")
    struct = dict(proj={"src": {"my_pkg": {"file.py": ""}}})

    # when the 'namespace' option is passed,
    struct, opts = get_default_options(struct, opts)
    struct, opts = enforce_namespace_options(struct, opts)
    struct, opts = move_old_package(struct, opts)

    # then the old package should be moved
    assert not tmpfolder.join("proj/src/my_pkg/__init__.py").check()
    assert tmpfolder.join("proj/src/my/ns/my_pkg/__init__.py").check()


def test_pretend_move_old_package(tmpfolder, caplog, isolated_logger):
    # Given a package is already created without namespace
    create_project(project="proj", package="my_pkg")

    opts = parse_args(["proj", "-p", "my_pkg", "--namespace", "my.ns", "--pretend"])
    opts = process_opts(opts)
    logger.reconfigure(opts)
    struct = dict(proj={"src": {"my_pkg": {"file.py": ""}}})

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
    create_project(project="my-proj")
    assert tmpfolder.join("my-proj/src/my_proj").check()
    assert not tmpfolder.join("my-proj/src/my/ns").check()

    # when the project is updated with a namespace,
    create_project(
        project="my-proj",
        update=True,
        namespace="my.ns",
        extensions=[namespace.Namespace("namespace")],
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
