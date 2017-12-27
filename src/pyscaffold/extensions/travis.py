# -*- coding: utf-8 -*-
"""
Extension that generates configuration and script files for Travis CI.
"""
from __future__ import absolute_import

from ..templates import travis, travis_install
from ..api import Extension
from ..api import helpers


class Travis(Extension):
    """Generate Travis CI configuration files"""
    def activate(self, actions):
        return self.register(
            actions,
            self.add_files,
            after='define_structure')

    def add_files(self, struct, opts):
        """Add Travis specific files to the project structure."""

        files = {
            '.travis.yml': (travis(opts), helpers.NO_OVERWRITE),
            'tests': {
                'travis_install.sh': (travis_install(opts),
                                      helpers.NO_OVERWRITE)
            }
        }

        return helpers.merge(struct, {opts['project']: files}), opts
