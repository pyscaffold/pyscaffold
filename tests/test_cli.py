#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import pytest
from pyscaffold import cli

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_parse_args():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts['project'] == "my-project"


def test_main_with_nogit(nogit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        cli.main(args)


def test_main_with_git_not_configured(noconfgit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        cli.main(args)


def test_main_when_folder_exists(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    os.mkdir(args[0])
    with pytest.raises(RuntimeError):
        cli.main(args)


def test_main(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    assert os.path.exists(args[0])


def test_main_when_updating(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    args = ["--update", "my-project"]
    cli.main(args)
    assert os.path.exists(args[1])


def test_main_when_updating_with_wrong_setup(tmpdir, git_mock):  # noqa
    os.mkdir("my_project")
    open("my_project/setup.py", 'a').close()
    args = ["--update", "my_project"]
    with pytest.raises(RuntimeError):
        cli.main(args)


def test_main_when_updating_project_doesnt_exist(tmpdir, git_mock):  # noqa
    args = ["--update", "my_project"]
    with pytest.raises(RuntimeError):
        cli.main(args)


def test_main_with_license(tmpdir, git_mock):  # noqa
    args = ["my-project", "-l", "new-bsd"]
    cli.main(args)
    assert os.path.exists(args[0])


def test_run(tmpdir, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    cli.run()
    assert os.path.exists(sys.argv[1])


def test_overwrite_git_repo(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "my_project"]
    cli.run()
    with pytest.raises(SystemExit):
        cli.run()
    sys.argv = ["pyscaffold", "--force", "my_project"]
    cli.run()


def test_overwrite_dir(tmpdir):  # noqa
    os.mkdir("my_project")
    sys.argv = ["pyscaffold", "--force", "my_project"]
    cli.run()


def test_django_proj(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-django", "my_project"]
    cli.run()


def test_with_travis(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-travis", "my_project"]
    cli.run()


def test_with_namespaces(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-namespace", "com.blue_yonder",
                "my_project"]
    cli.run()
    assert os.path.exists("my_project/com/blue_yonder")


def test_get_default_opts():
    args = ["project", "-p", "package", "-d", "description"]
    opts = cli.parse_args(args)
    new_opts = cli.get_default_opts(opts['project'], **opts)
    assert "author" not in opts
    assert "author" in new_opts


def test_get_defaults_opts_with_cookiecutter():
    args = ["project", "--with-cookiecutter", "http://..."]
    opts = cli.parse_args(args)
    new_opts = cli.get_default_opts(opts['project'], **opts)
    assert new_opts["force"]


def test_api(tmpdir):  # noqa
    opts = cli.get_default_opts('created_proj_with_api')
    cli.create_project(opts)
    assert os.path.exists('created_proj_with_api')


def test_api_with_cookiecutter(tmpdir):  # noqa
    template = 'https://github.com/audreyr/cookiecutter-pypackage.git'
    opts = cli.get_default_opts('created_proj_with_api',
                                cookiecutter_template=template)
    cli.create_project(opts)
    assert os.path.exists('created_proj_with_api')
