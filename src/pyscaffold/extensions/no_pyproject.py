"""
Extension that omits the creation of file `pyproject.toml`.

Since the isolated builds with PEP517/PEP518 are not completely backward compatible,
this extension provides an escape hatch for people that want to maintain the legacy
behaviour.

.. warning::
   This extension is **transitional** and will be removed in future versions of
   PyScaffold.
   Once support for isolated builds stabilises, the Python
   community will likely move towards using them more exclusively.
"""

from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from . import Extension


class NoPyProject(Extension):
    """Do not include a pyproject.toml file in the project root, and thus avoid isolated
    builds as defined in PEP517/518 [not recommended]
    """

    name = "no_pyproject"

    def activate(self, actions: List[Action]) -> List[Action]:
        actions = self.register(actions, ensure_option, before="get_default_options")
        return self.register(actions, remove_files, after="define_structure")


def ensure_option(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Make option available in non-CLI calls (used by other parts of PyScaffold)"""
    return struct, {**opts, "pyproject": False, "isolated_build": False}


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    struct = structure.reject(struct, "pyproject.toml")
    return struct, opts
