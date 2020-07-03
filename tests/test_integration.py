# -*- coding: utf-8 -*-
"""Unittests for the integration part of PyScaffold"""

import os
from distutils.cmd import Command
from distutils.dist import Distribution

import pytest

from pyscaffold import integration
from pyscaffold.contrib.setuptools_scm.version import ScmVersion


def test_version2str():
    ver = ScmVersion("1.0", distance=0)
    ver_str = integration.version2str(ver)
    assert ver_str == "1.0"
    ver = ScmVersion("1.0", distance=1)
    ver_str = integration.version2str(ver)
    assert ver_str == "1.0.post0.dev1"
    ver = ScmVersion("1.0.dev0", distance=1)
    ver_str = integration.version2str(ver)
    assert ver_str == "1.0.post0.dev1"


def test_local_version2str():
    ver = ScmVersion("1.0", dirty=True, node="abcdef")
    ver_str = integration.local_version2str(ver)
    assert ver_str == "+abcdef.dirty"
    ver = ScmVersion("1.0", dirty=False)
    ver_str = integration.local_version2str(ver)
    assert ver_str == ""
    ver = ScmVersion("1.0", distance=1, dirty=True, node="abcdef")
    ver_str = integration.local_version2str(ver)
    assert ver_str == "+abcdef.dirty"
    ver = ScmVersion("1.0", distance=1, dirty=False, node="abcdef")
    ver_str = integration.local_version2str(ver)
    assert ver_str == "+abcdef"


def test_build_cmd_docs():
    cmd = integration.build_cmd_docs()
    assert issubclass(cmd, Command)


@pytest.mark.skipif(
    bool(os.environ.get("TRAVIS", None)), reason="Test fails on Travis for no reason!"
)
def test_build_cmd_docs_no_sphinx(nosphinx_mock):
    cmd = integration.build_cmd_docs()
    assert cmd.__name__ == "NoSphinx"


def test_pyscaffold_keyword():
    dist = Distribution()
    integration.pyscaffold_keyword(dist, "use_pyscaffold", True)
