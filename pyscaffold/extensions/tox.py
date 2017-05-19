# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for the Tox test automation tool.
"""
from __future__ import absolute_import

from ..templates import tox as tox_ini


def augment_cli(parser):
    """Add an option to parser that enables the Travis extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument(
        "--with-tox",
        dest="extensions",
        action="append_const",
        const=extend_project,
        help="generate Tox configuration file")


def extend_project(scaffold):
    """Add Tox specific files to the project structure."""

    opts = scaffold.options

    files = {
        'tox.ini': (tox_ini(opts), scaffold.NO_OVERWRITE)
    }

    scaffold.merge_structure({opts['project']: files})
