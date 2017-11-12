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


def extend_project(actions, helpers):
    """Register an action responsible for adding tox files to project."""

    def add_files(struct, opts):
        """Add Tox specific files to the project structure."""

        files = {
            'tox.ini': (tox_ini(opts), helpers.NO_OVERWRITE)
        }

        return (helpers.merge(struct, {opts['project']: files}), opts)

    return helpers.register(actions, add_files)
