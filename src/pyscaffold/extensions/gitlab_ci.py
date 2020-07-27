"""
Extension that generates configuration and script files for GitLab CI.
"""

from ..api import helpers
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension


class GitLab(Extension):
    """Generate GitLab CI configuration files"""

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(actions, self.add_files, after="define_structure")

    def add_files(self, struct, opts):
        """Add .gitlab-ci.yml file to structure

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {".gitlab-ci.yml": (get_template("gitlab_ci"), no_overwrite())}

        return helpers.merge(struct, files), opts
