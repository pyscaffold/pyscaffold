#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import exists as path_exists

import pytest

from pyscaffold.api import create_project
from pyscaffold.cli import parse_args, run
from pyscaffold.extensions import namespace
from pyscaffold.extensions.namespace import add_namespace
from pyscaffold.utils import prepare_namespace


def test_add_namespace():
    args = ["project",
            "-p", "package",
            "--with-namespace", "com.blue_yonder"]
    opts = parse_args(args)
    opts['namespace'] = prepare_namespace(opts['namespace'])
    struct = {"project": {"package": {"file1": "Content"}}}
    ns_struct, _ = add_namespace(struct, opts)
    assert ["project"] == list(ns_struct.keys())
    assert "package" not in list(ns_struct.keys())
    assert ["com"] == list(ns_struct["project"].keys())
    assert {"blue_yonder", "__init__.py"} == set(
        ns_struct["project"]["com"].keys())
    assert "package" in list(ns_struct["project"]["com"]["blue_yonder"].keys())


def test_create_project_with_namespace(tmpfolder):
    # Given options with the namespace extension,
    opts = dict(project="my-proj", namespace="ns.ns2",
                extensions=[namespace.extend_project])

    # when the project is created,
    create_project(opts)

    # then nested structure should exist
    assert path_exists("my-proj/ns/__init__.py")
    assert path_exists("my-proj/ns/ns2/__init__.py")
    assert path_exists("my-proj/ns/ns2/my_proj/__init__.py")
    # and plain structure should not exist
    assert not path_exists("my-proj/my_proj/__init__.py")


def test_create_project_with_empty_namespace(tmpfolder):
    for j, ns in enumerate(["", None, False]):
        # Given options with the namespace extension,
        opts = dict(project="my-proj{}".format(j), namespace=ns,
                    extensions=[namespace.extend_project])

        # when the project is created,
        create_project(opts)

        # then plain structure should exist
        assert path_exists("my-proj{}/my_proj{}/__init__.py".format(j, j))


def test_create_project_without_namespace(tmpfolder):
    # Given options without the namespace extension,
    opts = dict(project="proj")

    # when the project is created,
    create_project(opts)

    # then plain structure should exist
    assert path_exists("proj/proj/__init__.py")


def test_cli_with_namespace(tmpfolder):  # noqa
    # Given the command line with the namespace option,
    sys.argv = ["pyscaffold", "proj", "--with-namespace", "ns"]

    # when pyscaffold runs,
    run()

    # then namespace package should exist
    assert path_exists("proj/ns/__init__.py")
    assert path_exists("proj/ns/proj/__init__.py")


def test_cli_with_empty_namespace(tmpfolder, capsys):  # noqa
    # Given the command line with the namespace option,
    sys.argv = ["pyscaffold", "proj", "--with-namespace"]

    # when pyscaffold runs,
    with pytest.raises(SystemExit):
        run()

    # then an error occurs
    _, err = capsys.readouterr()
    assert 'expected one argument' in err


def test_cli_without_namespace(tmpfolder):  # noqa
    # Given the command line without the namespace option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then namespace files should not exist
    assert not path_exists("proj/ns/__init__.py")
