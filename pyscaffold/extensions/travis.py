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


def extend_project(actions, helpers):
    """Register an action responsible for adding travis files to project."""

    def add_files(struct, opts):
        """Add Travis specific files to the project structure."""

        files = {
            '.travis.yml': (travis(opts), helpers.NO_OVERWRITE),
            'tests': {
                'travis_install.sh': (travis_install(opts),
                                      helpers.NO_OVERWRITE)
            }
        }

        return (helpers.merge(struct, {opts['project']: files}), opts)

    return helpers.register(actions, add_files)
