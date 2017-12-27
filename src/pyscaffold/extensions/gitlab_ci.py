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
        return self.register(
            actions,
            self.add_files,
            after='define_structure')

    def add_files(self, structure, opts):
        files = {
            '.gitlab-ci.yml': (gitlab_ci(opts), helpers.NO_OVERWRITE)
            }

        return helpers.merge(structure, {opts['project']: files}), opts
