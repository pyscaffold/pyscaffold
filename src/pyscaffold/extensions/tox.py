# -*- coding: utf-8 -*-
"""
Extension that generates configuration files for the Tox test automation tool.
"""

from ..api import Extension, helpers
from ..operations import no_overwrite
from ..templates import get_template


class Tox(Extension):
    """Generate Tox configuration file"""

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(actions, self.add_files, after="define_structure")

    def add_files(self, struct, opts):
        """Add .tox.ini file to structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {"tox.ini": (get_template("tox_ini"), no_overwrite())}

        return helpers.merge(struct, files), opts
