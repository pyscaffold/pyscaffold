"""Extension that generates configuration for Cirrus CI."""
from argparse import ArgumentParser
from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension, include
from .pre_commit import PreCommit

TEMPLATE_FILE = "cirrus"


class Cirrus(Extension):
    """Add configuration file for Cirrus CI (includes `--pre-commit`)"""

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
    """Add .cirrus.yml to the file structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    files: Structure = {".cirrus.yml": (cirrus_descriptor, no_overwrite())}

    return structure.merge(struct, files), opts


def cirrus_descriptor(_opts: ScaffoldOpts) -> str:
    """Returns the rendered template"""
    return get_template(TEMPLATE_FILE).template  # no substitutions required
