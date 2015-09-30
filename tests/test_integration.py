# -*- coding: utf-8 -*-

"""Unittests for the integration part of PyScaffold"""

from __future__ import division, print_function, absolute_import

import os
from distutils.dist import Distribution
from distutils.cmd import Command

from pyscaffold import integration
from setuptools_scm.version import ScmVersion
import six
import pytest

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_version2str():
    ver = ScmVersion('1.0', distance=0)
    ver_str = integration.version2str(ver)
    assert ver_str == '1.0'
    ver = ScmVersion('1.0', distance=1)
    ver_str = integration.version2str(ver)
    assert ver_str == '1.0.post0.dev1'
    ver = ScmVersion('1.0.dev0', distance=1)
    ver_str = integration.version2str(ver)
    assert ver_str == '1.0.post0.dev1'


def test_local_version2str():
    ver = ScmVersion('1.0', dirty=True, node='abcdef')
    ver_str = integration.local_version2str(ver)
    assert ver_str == '+abcdef.dirty'
    ver = ScmVersion('1.0', dirty=False)
    ver_str = integration.local_version2str(ver)
    assert ver_str == ''
    ver = ScmVersion('1.0', distance=1, dirty=True, node='abcdef')
    ver_str = integration.local_version2str(ver)
    assert ver_str == '+abcdef.dirty'
    ver = ScmVersion('1.0', distance=1, dirty=False, node='abcdef')
    ver_str = integration.local_version2str(ver)
    assert ver_str == '+abcdef'


def test_build_cmd_docs():
    cmd = integration.build_cmd_docs()
    assert issubclass(cmd, Command)


@pytest.mark.skipif(six.PY2, reason="Tests fail on Travis for Python 2.7.3 for no"
                                    "reasons!")
def test_build_cmd_docs_no_sphinx(nosphinx_mock):  # noqa
    cmd = integration.build_cmd_docs()
    assert cmd.__name__ == 'NoSphinx'


def test_deactivate_pbr_authors_changelog():
    integration.deactivate_pbr_authors_changelog()
    assert os.environ['SKIP_GENERATE_AUTHORS'] == "1"
    assert os.environ['SKIP_WRITE_GIT_CHANGELOG'] == "1"


def test_pyscaffold_keyword():  # noqa
    dist = Distribution()
    integration.pyscaffold_keyword(dist, 'use_pyscaffold', True)
