"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: http://pre-commit.com
"""

from .. import structure
from ..log import logger
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension


class PreCommit(Extension):
    """Generate pre-commit configuration file"""

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        actions = self.register(actions, self.add_files, after="define_structure")
        return self.register(actions, self.instruct_user, before="report_done")

    @staticmethod
    def add_files(struct, opts):
        """Add .pre-commit-config.yaml file to structure

        Since the default template uses isort, this function also provides an
        initial version of .isort.cfg that can be extended by the user
        (it contains some useful skips, e.g. tox and venv)

        Args:
            struct (dict): project representation as (possibly) nested
                :obj:`dict`.
            opts (dict): given options, see :obj:`create_project` for
                an extensive list.

        Returns:
            struct, opts: updated project representation and options
        """
        files = {
            ".pre-commit-config.yaml": (
                get_template("pre-commit-config"),
                no_overwrite(),
            ),
            ".isort.cfg": (get_template("isort_cfg"), no_overwrite()),
        }

        return structure.merge(struct, files), opts

    @staticmethod
    def instruct_user(struct, opts):
        logger.warning(
            "\nA `.pre-commit-config.yaml` file was generated inside your "
            "project but in order to make sure the hooks will run, please "
            "don't forget to install the `pre-commit` package:\n\n"
            f"  cd {opts['project_path']}\n"
            "  # it is a good idea to create and activate a virtualenv here\n"
            "  pip install pre-commit\n"
            "  pre-commit install\n"
            "  # another good idea is update the hooks to the latest version\n"
            "  # pre-commit autoupdate\n\n"
            "You might also consider including similar instructions in your "
            "docs, to remind the contributors to do the same.\n"
        )

        return struct, opts
