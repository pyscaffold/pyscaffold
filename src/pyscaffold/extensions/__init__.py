"""
Built-in extensions for PyScaffold.
"""
import argparse
from typing import Type

from ..actions import register, unregister
from ..identification import dasherize, underscore


class Extension:
    """Base class for PyScaffold's extensions

    Args:
        name (str): How the extension should be named. Default: name of class
            By default, this value is used to create the activation flag in
            PyScaffold cli.

    Note:
        Please name your class using a CamelCased version of the name you use in the
        setuptools entrypoint.
    """

    mutually_exclusive = False
    persist = True
    """When ``True`` PyScaffold will store the extension in the PyScaffold's section of
    ``setup.cfg``. Useful for updates. Set to ``False`` if the extension should not be
    re-invoked on updates.
    """

    def __init__(self, name=None):
        self.name = name or underscore(self.__class__.__name__)

    @property
    def flag(self):
        return f"--{dasherize(self.name)}"

    def augment_cli(self, parser):
        """Augments the command-line interface parser

        A command line argument ``--FLAG`` where FLAG=``self.name`` is added
        which appends ``self.activate`` to the list of extensions. As help
        text the docstring of the extension class is used.
        In most cases this method does not need to be overwritten.

        Args:
            parser: current parser object
        """
        parser.add_argument(
            self.flag,
            dest="extensions",
            action="append_const",
            const=self,
            help=self.__doc__[0].lower() + self.__doc__[1:],
        )
        return self

    def activate(self, actions):
        """Activates the extension by registering its functionality

        Args:
            actions (list): list of action to perform

        Returns:
            list: updated list of actions
        """
        raise NotImplementedError(
            "Extension {} has no actions registered".format(self.name)
        )

    @staticmethod
    def register(*args, **kwargs):
        """Shortcut for :obj:`pyscaffold.actions.register`"""
        return register(*args, **kwargs)

    @staticmethod
    def unregister(*args, **kwargs):
        """Shortcut for :obj:`pyscaffold.actions.unregister`"""
        return unregister(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Just delegating to :obj:`self.activate`"""
        return self.activate(*args, **kwargs)


def include(*extensions: Extension) -> Type[argparse.Action]:
    """Create a custom :obj:`argparse.Action` that saves multiple extensions for
    activation.

    Args:
        *extensions: extension objects to be saved
    """

    class IncludeExtensions(argparse.Action):
        """Appends the given extensions to the extensions list."""

        def __call__(self, parser, namespace, values, option_string=None):
            ext_list = list(getattr(namespace, "extensions", []))
            namespace.extensions = ext_list + list(extensions)

    return IncludeExtensions


def store_with(*extensions: Extension) -> Type[argparse.Action]:
    """Create a custom :obj:`argparse.Action` that stores the value of the given option
    in addition to saving the extension for activation.

    Args:
        *extensions: extension objects to be saved for activation
    """

    class AddExtensionAndStore(include(*extensions)):  # type: ignore
        """\
        Consumes the values provided, but also appends the given extension
        to the extensions list.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            super().__call__(parser, namespace, values, option_string)
            setattr(namespace, self.dest, values)

    return AddExtensionAndStore
