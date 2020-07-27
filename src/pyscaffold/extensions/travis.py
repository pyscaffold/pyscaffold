"""
Extension that generates configuration and script files for Travis CI.
"""

from .. import structure
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension


class Travis(Extension):
    """Generate Travis CI configuration files"""

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(actions, self.add_files, after="define_structure")

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
            ".travis.yml": (get_template("travis"), no_overwrite()),
            "tests": {
                "travis_install.sh": (get_template("travis_install"), no_overwrite())
            },
        }

        return structure.merge(struct, files), opts
