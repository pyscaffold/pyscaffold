"""This file is a fixture for TEST PURPOSES ONLY and uses an OUTDATED version of the
extensions API, and therefore will result in errors when imported
"""

from pyscaffold.api import Extension, helpers

# The module helpers was removed in version 4
# The class Extension was moved to the pyscaffold.extensions module


class FakeExtension(Extension):
    """Help text on commandline when running putup -h"""

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        actions = helpers.register(actions, self.action, after="create_structure")
        return actions

    def action(self, struct, opts):
        """Perform some actions that modifies the structure and options

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        print(self)
        return struct, opts
