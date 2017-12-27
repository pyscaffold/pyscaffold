# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: http://pre-commit.com
"""
from __future__ import absolute_import

from ..templates import pre_commit_config
from ..api import Extension
from ..api import helpers


class PreCommit(Extension):
    """Generate pre-commit configuration file"""
    def activate(self, actions):
        return self.register(
            actions,
            self.add_precommit_cfg,
            after='define_structure')

    def add_precommit_cfg(self, struct, opts):
        """Add pre-commit configuration files to the project structure."""

        files = {
            '.pre-commit-config.yaml': (
                pre_commit_config(opts), helpers.NO_OVERWRITE
            ),
        }

        return helpers.merge(struct, {opts['project']: files}), opts
