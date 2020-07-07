# -*- coding: utf-8 -*-
"""Extension that generates configuration for Cirrus CI."""
import argparse

from ..api import Extension, helpers
from ..templates import get_template
from .pre_commit import PreCommit
from .tox import Tox

TEMPLATE_FILE = "cirrus"


class Cirrus(Extension):
    """Add configuration file for Cirrus CI (includes `--tox` and `--pre-commit`)"""

    def augment_cli(self, parser):
        """Augments the command-line interface parser
        A command line argument ``--FLAG`` where FLAG=``self.name`` is added
        which appends ``self.activate`` to the list of extensions. As help
        text the docstring of the extension class is used.
        In most cases this method does not need to be overwritten.
        Args:
            parser: current parser object
        """
        help = self.__doc__[0].lower() + self.__doc__[1:]

        parser.add_argument(
            self.flag, help=help, nargs=0, dest="extensions", action=IncludeExtensions
        )
        return self

    def activate(self, actions):
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        return self.register(actions, add_files, after="define_structure")


class IncludeExtensions(argparse.Action):
    """Automatically activate tox and pre-commit together with cirrus."""

    def __call__(self, parser, namespace, _values, _option_string=None):
        extensions = [PreCommit("pre_commit"), Tox("tox"), Cirrus("cirrus")]

        namespace.extensions.extend(extensions)


def add_files(struct, opts):
    """Add .cirrus.yaml to the file structure

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    files = {".cirrus.yml": (cirrus_descriptor(opts), helpers.NO_OVERWRITE)}

    return helpers.merge(struct, {opts["project"]: files}), opts


def cirrus_descriptor(_opts):
    """Returns the rendered template"""
    return get_template(TEMPLATE_FILE).template  # no substitutions required
