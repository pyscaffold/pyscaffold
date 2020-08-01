"""
Extension that omits the creation of file `skeleton.py`
"""

from pathlib import PurePath as Path
from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from . import Extension


class NoSkeleton(Extension):
    """Omit creation of skeleton.py and test_skeleton.py"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(actions, remove_files, after="define_structure")


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Remove all skeleton files from structure

    Args:
        struct (Structure): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        typing.Tuple[structure.Structure, dict]:
            updated project representation and options
    """
    # Namespace is not yet applied so deleting from package is enough
    src = Path("src")
    struct = structure.reject(struct, src / opts["package"] / "skeleton.py")
    struct = structure.reject(struct, "tests/test_skeleton.py")
    return struct, opts
