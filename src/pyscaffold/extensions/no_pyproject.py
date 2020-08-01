"""
Extension that omits the creation of file `skeleton.py`
"""

from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from . import Extension


class NoPyProject(Extension):
    """Do not include a pyproject.toml file in the project root, and thus avoid isolated
    builds as defined in PEP517/518.
    """

    name = "no_pyproject"

    def activate(self, actions: List[Action]) -> List[Action]:
        return self.register(actions, remove_files, after="define_structure")


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    struct = structure.reject(struct, "pyproject.toml")
    return struct, opts
