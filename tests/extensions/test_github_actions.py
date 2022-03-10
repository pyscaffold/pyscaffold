#!/usr/bin/env python
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions.github_actions import GithubActions


def test_create_project_with_github_actions(tmpfolder):
    # Given options with the GithubActions extension,
    opts = dict(project_path="proj", extensions=[GithubActions()])

    # when the project is created,
    create_project(opts)

    # then files from GithubActions extension should exist
    assert path_exists("proj/.github/workflows/ci.yml")


def test_create_project_without_github_actions(tmpfolder):
    # Given options without the GithubActions extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then GithubActions files should not exist
    assert not path_exists("proj/.github/workflows/ci.yml")


def test_cli_with_github_actions(tmpfolder):
    # Given the command line with the GithubActions option,
    sys.argv = ["pyscaffold", "--github-actions", "proj"]

    # when pyscaffold runs,
    run()

    # then files from GithubActions and other extensions automatically added should
    # exist
    assert path_exists("proj/.github/workflows/ci.yml")
    assert path_exists("proj/tox.ini")
    assert path_exists("proj/.pre-commit-config.yaml")


def test_cli_with_github_actions_and_pretend(tmpfolder):
    # Given the command line with the GithubActions and pretend options
    sys.argv = ["pyscaffold", "--pretend", "--github-actions", "proj"]

    # when pyscaffold runs,
    run()

    # then GithubActions files should not exist
    assert not path_exists("proj/.github/workflows/ci.yml")
    # (or the project itself)
    assert not path_exists("proj")


def test_cli_without_github_actions(tmpfolder):
    # Given the command line without the GithubActions option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then GithubActions files should not exist
    assert not path_exists("proj/.github/workflows/ci.yml")
