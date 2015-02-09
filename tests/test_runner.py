#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os
import sys

import pytest
from pyscaffold import runner

from .fixtures import git_mock, noconfgit_mock, nogit_mock, tmpdir  # noqa

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_parse_args():
    args = ["my-project"]
    opts = runner.parse_args(args)
    assert opts.package == "my_project"


def test_main_with_nogit(nogit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_with_git_not_configured(noconfgit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_when_folder_exists(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    os.mkdir(args[0])
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    runner.main(args)
    assert os.path.exists(args[0])


def test_main_when_updating(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    runner.main(args)
    args = ["--update", "my-project"]
    runner.main(args)
    assert os.path.exists(args[1])


def test_main_when_updating_with_wrong_setup(tmpdir, git_mock):  # noqa
    os.mkdir("my_project")
    open("my_project/setup.py", 'a').close()
    args = ["--update", "my_project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_with_license(tmpdir, git_mock):  # noqa
    args = ["my-project", "-l", "new-bsd"]
    runner.main(args)
    assert os.path.exists(args[0])


def test_run(tmpdir, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    runner.run()
    assert os.path.exists(sys.argv[1])


def test_overwrite_git_repo(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "my_project"]
    runner.run()
    with pytest.raises(SystemExit):
        runner.run()
    sys.argv = ["pyscaffold", "--force", "my_project"]
    runner.run()


def test_overwrite_dir(tmpdir):  # noqa
    os.mkdir("my_project")
    sys.argv = ["pyscaffold", "--force", "my_project"]
    runner.run()


def test_django_proj(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-django", "my_project"]
    runner.run()


def test_with_numpydoc(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-numpydoc", "my_project"]
    runner.run()
    conffile = os.path.join(
        os.path.abspath(os.path.curdir), "my_project", "docs", "conf.py")
    conf = imp.load_source('conf', conffile)
    assert sorted(conf.extensions) == sorted(['sphinx.ext.autodoc',
                                              'sphinx.ext.intersphinx',
                                              'sphinx.ext.todo',
                                              'sphinx.ext.autosummary',
                                              'sphinx.ext.viewcode',
                                              'sphinx.ext.coverage',
                                              'sphinx.ext.doctest',
                                              'sphinx.ext.ifconfig',
                                              'sphinx.ext.pngmath',
                                              'numpydoc'])


def test_with_travis(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-travis", "my_project"]
    runner.run()


def test_prepare_namespace():
    namespaces = runner.prepare_namespace("com")
    assert namespaces == ["com"]
    namespaces = runner.prepare_namespace("com.blue_yonder")
    assert namespaces == ["com", "com.blue_yonder"]
    with pytest.raises(RuntimeError):
        runner.prepare_namespace("com.blue-yonder")


def test_with_namespaces(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-namespace", "com.blue_yonder",
                "my_project"]
    runner.run()
    assert os.path.exists("my_project/com/blue_yonder")
