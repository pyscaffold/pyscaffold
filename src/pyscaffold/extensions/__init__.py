"""
Built-in extensions for PyScaffold.
"""
import argparse
import sys
import textwrap
from typing import Callable, Iterable, List, Optional, Type

from ..actions import Action, register, unregister
from ..exceptions import ErrorLoadingExtension
from ..identification import dasherize, deterministic_sort, underscore

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import EntryPoint, entry_points  # pragma: no cover
else:
    from importlib_metadata import EntryPoint, entry_points  # pragma: no cover


ENTRYPOINT_GROUP = "pyscaffold.cli"

NO_LONGER_NEEDED = {"pyproject", "tox"}
"""Extensions that are no longer needed and are now part of PyScaffold itself"""

# TODO: NO_LONGER_SUPPORTED = {"no_pyproject"}


class Extension:
    """Base class for PyScaffold's extensions

    Args:
        name (str): How the extension should be named. Default: name of class
            By default, this value is used to create the activation flag in
            PyScaffold cli.

    See our docs on how to create extensions in:
    https://pyscaffold.org/en/latest/extensions.html

    Also check :obj:`~pyscaffold.actions`, :obj:`~pyscaffold.structure.Structure` and
    :obj:`~pyscaffold.operations.ScaffoldOpts` for more details.

    Note:
        Please name your class using a CamelCase version of the name you use in the
        setuptools entrypoint (alternatively you will need to overwrite the ``name``
        property to match the entrypoint name).
    """

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
        """Augments the command-line interface parser.

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

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activates the extension by registering its functionality

        Args:
            actions (List[Action]): list of action to perform

        Returns:
            List[Action]: updated list of actions
        """
        raise NotImplementedError(f"Extension {self.name} has no actions registered")

    register = staticmethod(register)
    """Shortcut for :obj:`pyscaffold.actions.register`"""

    unregister = staticmethod(unregister)
    """Shortcut for :obj:`pyscaffold.actions.unregister`"""

    def __call__(self, actions: List[Action]) -> List[Action]:
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


def iterate_entry_points(group=ENTRYPOINT_GROUP) -> Iterable[EntryPoint]:
    """Produces a generator yielding an EntryPoint object for each extension registered
    via `setuptools`_ entry point mechanism.

    This method can be used in conjunction with :obj:`load_from_entry_point` to filter
    the extensions before actually loading them.


    .. _setuptools: https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
    """  # noqa
    entries = entry_points()
    if hasattr(entries, "select"):
        # The select method was introduced in importlib_metadata 3.9 (and Python 3.10)
        # and the previous dict interface was declared deprecated
        return entries.select(group=group)  # type: ignore
    else:
        # TODO: Once Python 3.10 becomes the oldest version supported, this fallback and
        #       conditional statement can be removed.
        return (extension for extension in entries.get(group, []))  # type: ignore


def load_from_entry_point(entry_point: EntryPoint) -> Extension:
    """Carefully load the extension, raising a meaningful message in case of errors"""
    try:
        return entry_point.load()(entry_point.name)
    except Exception as ex:
        raise ErrorLoadingExtension(entry_point=entry_point) from ex


def list_from_entry_points(
    group: str = ENTRYPOINT_GROUP,
    filtering: Callable[[EntryPoint], bool] = lambda _: True,
) -> List[Extension]:
    """Produces a list of extension objects for each extension registered
    via `setuptools`_ entry point mechanism.

    Args:
        group: name of the setuptools' entry_point group where extensions is being
            registered
        filtering: function returning a boolean deciding if the entry point should be
            loaded and included (or not) in the final list. A ``True`` return means the
            extension should be included.

    .. _setuptools: https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
    """  # noqa
    return deterministic_sort(
        load_from_entry_point(e) for e in iterate_entry_points(group) if filtering(e)
    )
