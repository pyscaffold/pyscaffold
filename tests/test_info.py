import getpass
import os
import socket
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest
from configupdater import ConfigUpdater

from pyscaffold import actions, cli, exceptions, info, repo, structure, templates


def test_username_with_git(git_mock):
    username = info.username()
    assert isinstance(username, str)
    assert len(username) > 0


def test_username_with_no_git(nogit_mock):
    username = info.username()
    assert isinstance(username, str)
    assert getpass.getuser() == username


def test_username_error(git_mock, monkeypatch):
    fake_git = Mock(side_effect=exceptions.ShellCommandException)
    monkeypatch.setattr(info.shell, "git", fake_git)
    # on windows getpass might fail
    monkeypatch.setattr(info.getpass, "getuser", Mock(side_effect=SystemError))
    with pytest.raises(exceptions.GitNotConfigured):
        info.username()


def test_email_with_git(git_mock):
    email = info.email()
    assert "@" in email


def test_email_with_nogit(nogit_mock):
    email = info.email()
    assert socket.gethostname() == email.split("@")[1]


def test_email_error(git_mock, monkeypatch):
    fake_git = Mock(side_effect=exceptions.ShellCommandException)
    monkeypatch.setattr(info.shell, "git", fake_git)
    # on windows getpass might fail
    monkeypatch.setattr(info.getpass, "getuser", Mock(side_effect=SystemError))
    with pytest.raises(exceptions.GitNotConfigured):
        info.email()


def test_git_is_installed(git_mock):
    assert info.is_git_installed()


def test_git_is_wrongely_installed(nogit_mock):
    assert not info.is_git_installed()


def test_git_is_not_installed(nonegit_mock):
    assert not info.is_git_installed()


def test_is_git_configured(git_mock):
    assert info.is_git_configured()


def test_git_is_configured_via_env_vars(monkeypatch):
    monkeypatch.setenv("GIT_AUTHOR_NAME", "John Doe")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "johndoe@email.com")
    assert info.is_git_configured()


def test_is_git_not_configured(noconfgit_mock):
    assert not info.is_git_configured()


def test_check_git_not_installed(nonegit_mock):
    with pytest.raises(exceptions.GitNotInstalled):
        info.check_git()


def test_check_git_not_configured(noconfgit_mock):
    with pytest.raises(exceptions.GitNotConfigured):
        info.check_git()


def test_check_git_installed_and_configured(git_mock):
    info.check_git()


def test_project_without_args(tmpfolder):
    old_args = [
        "my_project",
        "-u",
        "http://www.blue-yonder.com/",
        "-d",
        "my description",
    ]
    cli.main(old_args)
    args = ["my_project"]
    opts = cli.parse_args(args)
    new_opts = info.project(opts)
    assert new_opts["url"] == "http://www.blue-yonder.com/"
    assert new_opts["package"] == "my_project"
    assert new_opts["license"] == "MIT"
    assert new_opts["description"] == "my description"


def test_project_with_args(tmpfolder):
    old_args = [
        "my_project",
        "-u",
        "http://www.blue-yonder.com/",
        "-d",
        "my description",
    ]
    cli.main(old_args)
    args = ["my_project", "-u", "http://www.google.com/", "-d", "other description"]
    opts = cli.parse_args(args)
    new_opts = info.project(opts)
    assert new_opts["url"] == "http://www.google.com/"
    assert new_opts["package"] == "my_project"
    assert new_opts["description"] == "other description"


def test_project_with_no_setup(tmpfolder):
    os.mkdir("my_project")
    args = ["my_project"]
    opts = cli.parse_args(args)
    with pytest.raises(FileNotFoundError):
        info.project(opts)


def test_project_with_wrong_setup(tmpfolder):
    os.mkdir("my_project")
    open("my_project/setup.py", "a").close()
    args = ["my_project"]
    opts = cli.parse_args(args)
    with pytest.raises(FileNotFoundError):
        info.project(opts)


def test_project_old_setupcfg(tmpfolder):
    demoapp = Path(__file__).parent / "demoapp"
    with pytest.raises(exceptions.PyScaffoldTooOld):
        info.project({}, config_path=demoapp)


def test_project_extensions_not_found(tmpfolder):
    _, opts = actions.get_default_options({}, {})
    cfg = ConfigUpdater().read_string(templates.setup_cfg(opts))
    cfg["pyscaffold"]["extensions"] = "x_foo_bar_x"
    (tmpfolder / "setup.cfg").write(str(cfg))
    with pytest.raises(exceptions.ExtensionNotFound) as exc:
        info.project(opts)
    assert "x_foo_bar_x" in str(exc.value)


@pytest.mark.no_fake_config_dir
def test_config_dir_error(monkeypatch):
    # no_fake_config_dir => avoid previous mock of config_dir

    # If for some reason something goes wrong when trying to find the config dir
    user_config_dir_mock = Mock(side_effect=SystemError)
    monkeypatch.setattr(info.appdirs, "user_config_dir", user_config_dir_mock)
    # And no default value is given
    # Then an error should be raised
    with pytest.raises(exceptions.ImpossibleToFindConfigDir):
        print("config_dir", info.config_dir())
        user_config_dir_mock.assert_called_once()


def test_config_file_default(monkeypatch):
    # When config_dir does not find the correct config directory
    monkeypatch.setattr(info, "config_dir", Mock(return_value=None))
    # And there are a default file
    demoapp_setup = Path(__file__).parent / "demoapp" / "setup.cfg"
    # Then the default file should be returned
    assert info.config_file(default=demoapp_setup) == demoapp_setup


def test_best_fit_license():
    # If the name matches => return the name
    for license in templates.licenses.keys():
        assert info.best_fit_license(license) == license
    # Lower case
    assert info.best_fit_license("0bsd") == "0BSD"
    # No dashes
    assert info.best_fit_license("mpl2") == "MPL-2.0"
    assert info.best_fit_license("gpl2") == "GPL-2.0-only"
    assert info.best_fit_license("gpl3") == "GPL-3.0-only"
    assert info.best_fit_license("bsd2") == "BSD-2-Clause"
    assert info.best_fit_license("bsd3") == "BSD-3-Clause"
    # Popular nicknames
    assert info.best_fit_license("apache") == "Apache-2.0"
    assert info.best_fit_license("artistic") == "Artistic-2.0"
    assert info.best_fit_license("affero") == "AGPL-3.0-only"
    assert info.best_fit_license("eclipse") == "EPL-1.0"
    assert info.best_fit_license("bsd0") == "0BSD"
    assert info.best_fit_license("new-bsd") == "BSD-3-Clause"
    assert info.best_fit_license("simple-bsd") == "BSD-2-Clause"
    assert info.best_fit_license("cc0") == "CC0-1.0"
    assert info.best_fit_license("none") == "Proprietary"
    assert info.best_fit_license("public-domain") == "Unlicense"
    # Or later vs only
    assert info.best_fit_license("gpl3-only") == "GPL-3.0-only"
    assert info.best_fit_license("gpl2-later") == "GPL-2.0-or-later"
    # Default
    assert info.best_fit_license("") == "MIT"


def test_dirty_workspace(tmpfolder):
    project = "my_project"
    struct = {"dummyfile": "NO CONTENT"}
    structure.create_structure(struct, dict(project_path=project))
    repo.init_commit_repo(project, struct)
    path = tmpfolder / project
    assert info.is_git_workspace_clean(path)
    with open(str(path / "dummyfile"), "w") as fh:
        fh.write("CHANGED\n")
    assert not info.is_git_workspace_clean(path)
