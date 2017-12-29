# -*- coding: utf-8 -*-
"""
Extension that generates configuration and script files for GitLab CI.
"""
from __future__ import absolute_import

from ..templates import gitlab_ci
from ..api import Extension
from ..api import helpers


class GitLab(Extension):
    """Generate GitLab CI configuration files"""
    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(
            actions,
            self.add_files,
            after='define_structure')

    def add_files(self, struct, opts):
        """Add .gitlab-ci.yml file to structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {
            '.gitlab-ci.yml': (gitlab_ci(opts), helpers.NO_OVERWRITE)
            }

        return helpers.merge(struct, {opts['project']: files}), opts
