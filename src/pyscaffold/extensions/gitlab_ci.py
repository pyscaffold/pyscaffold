# -*- coding: utf-8 -*-
"""
Extension that generates configuration and script files for GitLab CI.
"""
from __future__ import absolute_import

from ..templates import gitlab_ci


def augment_cli(parser):
    """Add an option to parser that enables the GitLab CI extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument("--gitlab",
                        dest="extensions",
                        action="append_const",
                        const=extend_project,
                        help="generate GitLab CI configuration files")


def extend_project(actions, helpers):
    """Add GitLab CI specific files to the project structure."""

    def add_gitlab_file(structure, opts):
        files = {
            '.gitlab-ci.yml': (gitlab_ci(opts), helpers.NO_OVERWRITE)
            }

        return helpers.merge(structure, {opts['project']: files}), opts

    return helpers.register(actions, add_gitlab_file)
