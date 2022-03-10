#!/usr/bin/env python
import sys
from os.path import exists as path_exists

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions.gitlab_ci import GitLab


def test_create_project_with_gitlab_ci(tmpfolder):
    # Given options with the GitLab extension,
    opts = dict(project_path="proj", extensions=[GitLab()])

    # when the project is created,
    create_project(opts)

    # then files from GitLab extension should exist
    assert path_exists("proj/.gitlab-ci.yml")


def test_create_project_without_gitlab_ci(tmpfolder):
    # Given options without the GitLab extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then GitLab files should not exist
    assert not path_exists("proj/.gitlab-ci.yml")


def test_cli_with_gitlab_ci(tmpfolder):
    # Given the command line with the GitLab option,
    sys.argv = ["pyscaffold", "--gitlab", "proj"]

    # when pyscaffold runs,
    run()

    # then files from GitLab and other extensions automatically added should
    # exist
    assert path_exists("proj/.gitlab-ci.yml")
    assert path_exists("proj/tox.ini")
    assert path_exists("proj/.pre-commit-config.yaml")


def test_cli_with_gitlab_ci_and_pretend(tmpfolder):
    # Given the command line with the GitLab and pretend options
    sys.argv = ["pyscaffold", "--pretend", "--gitlab", "proj"]

    # when pyscaffold runs,
    run()

    # then GitLab files should not exist
    assert not path_exists("proj/.gitlab-ci.yml")
    # (or the project itself)
    assert not path_exists("proj")


def test_cli_without_gitlab_ci(tmpfolder):
    # Given the command line without the GitLab option,
    sys.argv = ["pyscaffold", "proj"]

    # when pyscaffold runs,
    run()

    # then GitLab files should not exist
    assert not path_exists("proj/.gitlab-ci.yml")
