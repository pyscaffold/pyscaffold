from pathlib import Path

from pyscaffold.api import create_project
from pyscaffold.cli import run
from pyscaffold.extensions.no_pyproject import NoPyProject


def test_create_project_wit_no_pyproject(tmpfolder):
    # Given options with the no_pyproject extension,
    opts = dict(project_path="proj", extensions=[NoPyProject()])

    # when the project is created,
    _, opts = create_project(opts)

    # then file should not exist
    assert not Path("proj/pyproject.toml").exists()

    assert opts["isolated_build"] is False


def test_create_project_without_no_pyproject(tmpfolder):
    # Given options without the no_pyproject extension,
    opts = dict(project_path="proj")

    # when the project is created,
    _, opts = create_project(opts)

    # then file should exist
    assert Path("proj/pyproject.toml").exists()

    assert opts["isolated_build"] is True


def test_cli_with_no_pyproject(tmpfolder):
    # Given the command line with the no-pyproject option,
    # when pyscaffold runs,
    run(["--no-pyproject", "proj"])

    # then file should not exist
    assert not Path("proj/pyproject.toml").exists()


def test_cli_with_no_pyproject_and_pretend(tmpfolder):
    # Given the command line with the no-pyproject and pretend options,
    # when pyscaffold runs,
    run(["--pretend", "--no-pyproject", "proj"])

    # then file should not exist (or the project itself)
    assert not Path("proj/pyproject.toml").exists()
    assert not Path("proj").exists()


def test_cli_without_no_pyproject(tmpfolder):
    # Given the command line without the no-pyproject option,
    # when pyscaffold runs,
    run(["--no-pyproject", "proj"])

    # then file should not exist
    assert not Path("proj/pyproject.toml").exists()
