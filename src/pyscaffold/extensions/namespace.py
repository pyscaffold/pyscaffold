"""
Extension that adjust project file tree to include a namespace package.

This extension adds a **namespace** option to
:obj:`~pyscaffold.api.create_project` and provides correct values for the
options **root_pkg** and **namespace_pkg** to the following functions in the
action list.
"""

import os
from pathlib import Path
from typing import List, cast

from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..exceptions import InvalidIdentifier
from ..file_system import chdir, move
from ..identification import is_valid_identifier
from ..log import logger
from ..operations import remove
from . import Extension, store_with


class Namespace(Extension):
    """Add a namespace (container package) to the generated package."""

    def augment_cli(self, parser):
        """Add an option to parser that enables the namespace extension.

        Args:
            parser (argparse.ArgumentParser): CLI parser object
        """
        parser.add_argument(
            self.flag,
            dest=self.name,
            default=None,
            action=store_with(self),
            metavar="NS1[.NS2]",
            help="put your project inside a namespace package "
            "(default: use no namespace)",
        )
        return self

    def activate(self, actions: List[Action]) -> List[Action]:
        """Register an action responsible for adding namespace to the package.

        Args:
            actions: list of actions to perform

        Returns:
            list: updated list of actions
        """
        actions = self.register(
            actions, enforce_namespace_options, after="get_default_options"
        )

        actions = self.register(actions, add_namespace, before="version_migration")

        return self.register(actions, move_old_package, after="create_structure")


def prepare_namespace(namespace_str: str) -> List[str]:
    """Check the validity of namespace_str and split it up into a list

    Args:
        namespace_str: namespace, e.g. "com.blue_yonder"

    Returns:
        list of namespaces, e.g. ["com", "com.blue_yonder"]

    Raises:
          :obj:`InvalidIdentifier` : raised if namespace is not valid
    """
    namespaces = namespace_str.split(".") if namespace_str else list()
    for namespace in namespaces:
        if not is_valid_identifier(namespace):
            raise InvalidIdentifier(f"{namespace} is not a valid namespace package.")
    return [".".join(namespaces[: i + 1]) for i in range(len(namespaces))]


def enforce_namespace_options(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Make sure options reflect the namespace usage."""
    opts.setdefault("namespace", "")

    if opts["namespace"]:
        opts["ns_list"] = prepare_namespace(opts["namespace"])
        opts["root_pkg"] = opts["ns_list"][0]
        opts["qual_pkg"] = ".".join([opts["ns_list"][-1], opts["package"]])
        opts["namespace"] = opts["namespace"].strip()

    return struct, opts


def add_namespace(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Prepend the namespace to a given file structure

    Args:
        struct: directory structure as dictionary of dictionaries
        opts: options of the project

    Returns:
        Directory structure as dictionary of dictionaries and input options
    """
    if not opts.get("namespace"):
        msg = "Using the `Namespace` extension with an empty namespace string/None. "
        msg += "You can try a valid string with the `--namespace` option in `putup` "
        msg += "(PyScaffold CLI) the arguments in `create_project` (PyScaffold API)."
        logger.warning(msg)
        return struct, opts

    namespace = opts["ns_list"][-1].split(".")
    base_struct = struct
    struct = cast(Structure, base_struct["src"])  # recursive types not supported yet
    pkg_struct = cast(Structure, struct[opts["package"]])
    del struct[opts["package"]]
    for sub_package in namespace:
        struct[sub_package] = {"__init__.py": ("", remove)}  # convert to PEP420
        struct = cast(Structure, struct[sub_package])
    struct[opts["package"]] = pkg_struct

    return base_struct, opts


def move_old_package(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Move old package that may be eventually created without namespace

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries and input options
    """
    project_path = Path(opts.get("project_path", "."))
    with chdir(project_path, log=True, **opts):
        old_path = Path("src", opts["package"])
        namespace_path = opts["qual_pkg"].replace(".", os.sep)
        target = Path("src", namespace_path)

        old_exists = opts["pretend"] or old_path.is_dir()
        #  ^  When pretending, pretend also an old folder exists
        #     to show a worst case scenario log to the user...

        if old_exists and opts["qual_pkg"] != opts["package"]:
            if not opts["pretend"]:
                logger.warning(
                    "\nA folder %r exists in the project directory, and it "
                    "is likely to have been generated by a PyScaffold "
                    "extension or manually by one of the current project "
                    "authors.\n"
                    "Moving it to %r, since a namespace option was passed.\n"
                    "Please make sure to edit all the files that depend on  "
                    "this package to ensure the correct location.\n",
                    opts["package"],
                    namespace_path,
                )

            move(old_path, target=target, log=True, pretend=opts["pretend"])

    return struct, opts
