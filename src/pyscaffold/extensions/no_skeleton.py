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
            self.remove_skeleton,
            after='define_structure')

    def remove_skeleton(self, struct, opts):
        file = [opts['project'], 'src', opts['package'], 'skeleton.py']
        struct = helpers.reject(struct, file)
        return struct, opts
