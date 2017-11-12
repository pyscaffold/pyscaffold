# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: http://pre-commit.com
"""
from __future__ import absolute_import

from ..templates import pre_commit_config


def augment_cli(parser):
    """Add an option to parser that enables the `pre-commit`_ extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object

    .. _pre-commit: http://pre-commit.com
    """

    parser.add_argument(
        "--with-pre-commit",
        dest="extensions",
        action="append_const",
        const=extend_project,
        help="generate pre-commit configuration file")


def extend_project(actions, helpers):
    """Register an action responsible for adding specific files to project."""

    def add_files(struct, opts):
        """Add pre-commit configuration files to the project structure."""

        files = {
            '.pre-commit-config.yaml': (
                pre_commit_config(opts), helpers.NO_OVERWRITE
            ),
        }

        return (helpers.merge(struct, {opts['project']: files}), opts)

    return helpers.register(actions, add_files)
