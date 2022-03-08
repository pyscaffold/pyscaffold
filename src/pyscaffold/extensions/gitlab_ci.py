"""
Extension that generates configuration and script files for GitLab CI.
"""
from argparse import ArgumentParser
from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension, include
from .pre_commit import PreCommit


class GitLab(Extension):
    """Generate GitLab CI configuration files"""

    def augment_cli(self, parser: ArgumentParser):
        """Augments the command-line interface parser.
        See :obj:`~pyscaffold.extension.Extension.augment_cli`.
        """
        parser.add_argument(
            self.flag, help=self.help_text, nargs=0, action=include(PreCommit(), self)
        )
        return self

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension, see :obj:`~pyscaffold.extension.Extension.activate`."""
        return self.register(actions, add_files, after="define_structure")


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add .gitlab-ci.yml file to structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    files: ScaffoldOpts = {
        ".gitlab-ci.yml": (get_template("gitlab_ci"), no_overwrite())
    }

    return structure.merge(struct, files), opts
