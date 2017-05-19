# -*- coding: utf-8 -*-
"""
Extension that generates configuration and script files for Travis CI.
"""
from __future__ import absolute_import

from ..templates import travis, travis_install


def augment_cli(parser):
    """Add an option to parser that enables the Travis extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument(
        "--with-travis",
        dest="extensions",
        action="append_const",
        const=extend_project,
        help="generate Travis configuration files")


def extend_project(scaffold):
    """Add Travis specific files to the project structure."""

    opts = scaffold.options

    files = {
        '.travis.yml': (travis(opts), scaffold.NO_OVERWRITE),
        'tests': {
            'travis_install.sh': (travis_install(opts), scaffold.NO_OVERWRITE)
        }
    }

    scaffold.merge_structure({opts['project']: files})
