"""
Extension that generates configuration files for the Tox test automation tool.
"""

from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension


class Tox(Extension):
    """Generate Tox configuration file"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension, see :obj:`~pyscaffold.extension.Extension.activate`."""
        return self.register(actions, add_files, after="define_structure")


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add .tox.ini file to structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    files: Structure = {"tox.ini": (get_template("tox_ini"), no_overwrite())}

    return structure.merge(struct, files), opts
