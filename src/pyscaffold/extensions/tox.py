# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for the Tox test automation tool.
"""
from __future__ import absolute_import

from ..templates import tox as tox_ini
from ..api import Extension
from ..api import helpers


class Tox(Extension):
    """Generate Tox configuration file"""
    def activate(self, actions):
        return self.register(
            actions,
            self.add_files,
            after='define_structure')

    def add_files(self, struct, opts):
        """Add Tox specific files to the project structure."""

        files = {
            'tox.ini': (tox_ini(opts), helpers.NO_OVERWRITE)
        }

        return helpers.merge(struct, {opts['project']: files}), opts
