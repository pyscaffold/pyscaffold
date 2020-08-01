"""
Built-in extensions for PyScaffold.
"""
import argparse
import textwrap
from typing import List, Optional, Type

from ..actions import Action, register, unregister
from ..identification import dasherize, underscore


class Extension:
    """Base class for PyScaffold's extensions

    Args:
        name (str): How the extension should be named. Default: name of class
            By default, this value is used to create the activation flag in
            PyScaffold cli.

    Note:
        Please name your class using a CamelCase version of the name you use in the
        setuptools entrypoint (alternatively you will need to overwrite the ``name``
        property to match the entrypoint name).
    """

    mutually_exclusive = False
    persist = True
    """When ``True`` PyScaffold will store the extension in the PyScaffold's section of
    ``setup.cfg``. Useful for updates. Set to ``False`` if the extension should not be
    re-invoked on updates.
    """

    def __init__(self, name: Optional[str] = None):
        self._name = name or underscore(self.__class__.__name__)

    @property
    def name(self):
        return self._name

    @property
    def flag(self) -> str:
        return f"--{dasherize(self.name)}"

    @property
    def help_text(self) -> str:
        if self.__doc__ is None:
            raise NotImplementedError("Please provide a help text for your extension")

        doc = textwrap.dedent(self.__doc__)
        return doc[0].lower() + doc[1:]

    def augment_cli(self, parser: argparse.ArgumentParser):
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
            help=self.help_text,
        )
        return self

    def activate(self, actions: List[Action]):
        """Activates the extension by registering its functionality

        Args:
            actions: list of action to perform

        Returns:
            list: updated list of actions
        """
        raise NotImplementedError(
            "Extension {} has no actions registered".format(self.name)
        )

    register = staticmethod(register)
    """Shortcut for :obj:`pyscaffold.actions.register`"""

    unregister = staticmethod(unregister)
    """Shortcut for :obj:`pyscaffold.actions.unregister`"""

    def __call__(self, actions: List[Action]):
        """Just delegating to :obj:`self.activate`"""
        return self.activate(actions)


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
