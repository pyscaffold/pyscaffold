# -*- coding: utf-8 -*-
"""
Extension that omits the creation of file `skeleton.py`
"""

from pathlib import PurePath as Path

from ..api import Extension, helpers


class NoSkeleton(Extension):
    """Omit creation of skeleton.py and test_skeleton.py"""
    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(
            actions,
            self.remove_files,
            after='define_structure')

    def remove_files(self, struct, opts):
        """Remove all skeleton files from structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        # Namespace is not yet applied so deleting from package is enough
        file = Path(opts['project'], 'src', opts['package'], 'skeleton.py')
        struct = helpers.reject(struct, file)
        file = Path(opts['project'], 'tests', 'test_skeleton.py')
        struct = helpers.reject(struct, file)
        return struct, opts
