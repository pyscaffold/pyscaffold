# -*- coding: utf-8 -*-
"""
Extension that generates configuration and script files for Travis CI.
"""

from ..api import Extension, helpers
from ..templates import travis, travis_install


class Travis(Extension):
    """Generate Travis CI configuration files"""
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
        """Add some Travis files to structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {
            '.travis.yml': (travis(opts), helpers.NO_OVERWRITE),
            'tests': {
                'travis_install.sh': (travis_install(opts),
                                      helpers.NO_OVERWRITE)
            }
        }

        return helpers.merge(struct, {opts['project']: files}), opts
