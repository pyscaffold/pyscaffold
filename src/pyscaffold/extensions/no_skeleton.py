# -*- coding: utf-8 -*-
"""
Extension that omits the creation of file `skeleton.py`
"""

from ..api import Extension
from ..api import helpers


class NoSkeleton(Extension):
    """Omit creation of skeleton.py"""
    def activate(self, actions):
        return self.register(
            actions,
            self.remove_files,
            after='define_structure')

    def remove_files(self, struct, opts):
        pkgs = opts['qual_pkg'].split('.')
        file = [opts['project'], 'src'] + pkgs + ['skeleton.py']
        struct = helpers.reject(struct, file)
        file = [opts['project'], 'tests', 'test_skeleton.py']
        struct = helpers.reject(struct, file)
        return struct, opts
