"""
Extension that removes configuration files for the Tox test automation tool.
"""

from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from . import Extension


class NoTox(Extension):
    """Prevent a tox configuration file from being created"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension, see :obj:`~pyscaffold.extension.Extension.activate`."""
        return self.register(actions, remove_files, after="define_structure")


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Remove .tox.ini file to structure"""
    return structure.reject(struct, "tox.ini"), opts
