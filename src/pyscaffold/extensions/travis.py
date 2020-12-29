"""
Extension that generates configuration and script files for Travis CI.
"""

from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension


class Travis(Extension):
    """Generate Travis CI configuration files"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension, see :obj:`~pyscaffold.extension.Extension.activate`."""
        return self.register(actions, add_files, after="define_structure")


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add some Travis files to structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    files: Structure = {
        ".travis.yml": (get_template("travis"), no_overwrite()),
        "tests": {
            "travis_install.sh": (get_template("travis_install"), no_overwrite())
        },
    }

    return structure.merge(struct, files), opts
