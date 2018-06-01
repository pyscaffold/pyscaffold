# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: http://pre-commit.com
"""
from __future__ import absolute_import

from ..api import Extension, helpers
from ..log import logger
from ..templates import pre_commit_config


class PreCommit(Extension):
    """Generate pre-commit configuration file"""
    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return (
            self.register(actions, self.add_files, after='define_structure') +
            [self.instruct_user])

    @staticmethod
    def add_files(struct, opts):
        """Add .pre-commit-config.yaml file to structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {
            '.pre-commit-config.yaml': (
                pre_commit_config(opts), helpers.NO_OVERWRITE
            ),
        }

        return helpers.merge(struct, {opts['project']: files}), opts

    @staticmethod
    def instruct_user(struct, opts):
        logger.warning(
            '\nA `.pre-commit-config.yaml` file was generated inside your '
            'project but in order to make sure the hooks will run, please '
            'don\'t forget to install the `pre-commit` package:\n\n'
            '  cd %s\n'
            '  # you should consider creating/activating a virtualenv here\n'
            '  pip install pre-commit\n'
            '  pre-commit install\n\n'
            'You might also consider including similar instructions in your '
            'docs, to remind the contributors to do the same.\n',
            opts['project'])

        return struct, opts
