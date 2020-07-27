"""
Built-in extensions for PyScaffold.
"""
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

    def __init__(self, name=None, args=None):
        self.name = name or underscore(self.__class__.__name__)
        self.args = args

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
        help = self.__doc__[0].lower() + self.__doc__[1:]

        parser.add_argument(
            self.flag, help=help, dest="extensions", action="append_const", const=self
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
