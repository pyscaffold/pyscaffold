# -*- coding: utf-8 -*-

"""Unittests for the integration part of PyScaffold"""

from __future__ import division, print_function, absolute_import

import os
from distutils.cmd import Command

from pyscaffold import integration

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_build_cmd_docs():
    cmd = integration.build_cmd_docs()
    assert issubclass(cmd, Command)


def test_deactivate_pbr_authors_changelog():
    integration.deactivate_pbr_authors_changelog()
    assert os.environ['SKIP_GENERATE_AUTHORS'] == "1"
    # This is commented only due to a bug in PBR,
    # see https://bugs.launchpad.net/pbr/+bug/1467440
    # assert os.environ['SKIP_WRITE_GIT_CHANGELOG'] == "1"
