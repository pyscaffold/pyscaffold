"""
Extension that adjust project file tree to include a namespace package.

This extension adds a **namespace** option to
:obj:`~pyscaffold.api.create_project` and provides correct values for the
options **root_pkg** and **namespace_pkg** to the following functions in the
action list.
"""

import argparse
import os
from pathlib import Path

from ..api import helpers
from ..exceptions import InvalidIdentifier
from ..file_system import chdir, move
from ..identification import is_valid_identifier
from ..log import logger
from ..templates import get_template
from . import Extension


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
            action=create_namespace_parser(self),
            metavar="NS1[.NS2]",
            help="put your project inside a namespace package",
        )

    def activate(self, actions):
        """Register an action responsible for adding namespace to the package.

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        actions = helpers.register(
            actions, enforce_namespace_options, after="get_default_options"
        )

        actions = helpers.register(actions, add_namespace, before="version_migration")

        return helpers.register(actions, move_old_package, after="create_structure")


def create_namespace_parser(obj_ref):
    """Create a namespace parser.

    Args:
        obj_ref (Extension): object reference to the actual extension

    Returns:
        NamespaceParser: parser for namespace cli argument
    """

    class NamespaceParser(argparse.Action):
        """Consumes the values provided, but also appends the extension
           function to the extensions list.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            namespace.extensions.append(obj_ref)

            # Now the extra parameters can be stored
            setattr(namespace, self.dest, values)

            # save the namespace cli argument for later
            obj_ref.args = values

    return NamespaceParser


def prepare_namespace(namespace_str):
    """Check the validity of namespace_str and split it up into a list

    Args:
        namespace_str (str): namespace, e.g. "com.blue_yonder"

    Returns:
        [str]: list of namespaces, e.g. ["com", "com.blue_yonder"]

    Raises:
          :obj:`InvalidIdentifier` : raised if namespace is not valid
    """
    namespaces = namespace_str.split(".") if namespace_str else list()
    for namespace in namespaces:
        if not is_valid_identifier(namespace):
            raise InvalidIdentifier(
                "{} is not a valid namespace package.".format(namespace)
            )
    return [".".join(namespaces[: i + 1]) for i in range(len(namespaces))]


def enforce_namespace_options(struct, opts):
    """Make sure options reflect the namespace usage."""
    opts.setdefault("namespace", None)

    if opts["namespace"]:
        opts["ns_list"] = prepare_namespace(opts["namespace"])
        opts["root_pkg"] = opts["ns_list"][0]
        opts["qual_pkg"] = ".".join([opts["ns_list"][-1], opts["package"]])

    return struct, opts


def add_namespace(struct, opts):
    """Prepend the namespace to a given file structure

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries and input options
    """
    if not opts["namespace"]:
        return struct, opts

    namespace = opts["ns_list"][-1].split(".")
    base_struct = struct
    struct = base_struct["src"]
    pkg_struct = struct[opts["package"]]
    del struct[opts["package"]]
    for sub_package in namespace:
        struct[sub_package] = {"__init__.py": get_template("namespace")}
        struct = struct[sub_package]
    struct[opts["package"]] = pkg_struct

    return base_struct, opts


def move_old_package(struct, opts):
    """Move old package that may be eventually created without namespace

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries and input options
    """
    project_path = Path(opts.get("project_path", "."))
    with chdir(project_path, log=True):
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
