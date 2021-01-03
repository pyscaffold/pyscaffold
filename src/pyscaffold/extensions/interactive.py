"""Similarly to ``git rebase -i`` this extension allows users to interactively
choose which options apply to ``putup``, by editing a file filled with examples.

See :obj:`CONFIG` for more details on how to tweak the text generated in the interactive
mode.

.. versionadded:: 4.0
   *"interactive mode"* introduced as an **experimental** extension.

Warning:

    **NOTE FOR CONTRIBUTORS**:
    Due to the way :mod:`argparse` is written, it is not very easy to obtain information
    about which options and arguments a given parser is currently configured with.
    There are no public methods that allow inspection/reflection, and therefore in order
    to do so, one has to rely on a few non-public methods (according to Python's
    convention, the ones starting with a ``_`` symbol).
    Since :mod:`argparse` implementation is very stable and mature, these non-public
    method are very unlikely to change and, therefore, it is relatively safe to use
    these methods, however developers and maintainers have to be aware and pay attention
    to eventual breaking changes.
    The non-public functions are encapsulated in the functions :obj:`get_actions` and
    :obj:`format_args` in this file, in order to centralise the usage of non-public API.
"""
import os
import shlex
import textwrap
from argparse import Action, ArgumentParser
from collections import abc
from functools import lru_cache, reduce
from itertools import chain
from typing import List, Optional, Set

from .. import api, cli, file_system, shell, templates
from ..actions import ScaffoldOpts as Opts
from ..actions import get_default_options
from . import Extension
from . import list_from_entry_points as list_all_extensions

INDENT_LEVEL = 4
HEADER = templates.get_template("header_interactive")


CONFIG_KEY = "interactive"
CONFIG = {
    "ignore": ["--help", "--version"],
    "comment": ["--verbose", "--very-verbose"],
}
"""Configuration for the options that are not associated with an extension class.
This dict value consist of a set of metadata organised as follows:

- Each value must be a list of "long" :obj:`argparse` option strings (e.g. `"--help"`
  instead of `"-h"`).
- Each key implies on a different interpretation for the metadata:

    - ``"ignore"``: Options that should be simply ignored when creating examples
    - ``"comment"``: Options that should be commented when creating examples,
      even if they appear in the original :obj:`sys.argv`.

Extension classes (or instances) can also provide configurations by defining a
``interactive`` attribute assigned to a similar :obj:`dict` object.
"""


@lru_cache(maxsize=2)
def get_config(kind: str) -> Set[str]:
    """Get configurations that will be used for generating examples
    (from both :obj:`CONFIG` and the ``interactive`` attribute of each extension).

    The ``kind`` argument can assume the same values as the :obj:`CONFIG` keys.

    This function is cached to improve performance. Call ``get_config.__wrapped__`` to
    bypass the cache (or ``get_config.cache_clear``, see :obj:`functools.lru_cache`).
    """
    # TODO: when `python_requires >= 3.8` use Literal["ignore", "comment"] instead of
    #       str for type annotation of kind
    configurable = CONFIG.keys()
    assert kind in configurable
    initial_value = set(CONFIG[kind])  # A set avoid repeated flags
    empty_config: dict = {k: [] for k in configurable}  # Same shape as CONFIG

    def _merge_config(accumulated_config, extension):
        # The main idea is to collect all the configuration dicts from the extensions
        # (`interactive` attribute) and merge them with CONFIG, avoiding repetitions
        extension_config_dict = getattr(extension, CONFIG_KEY, empty_config)
        return accumulated_config.union(set(extension_config_dict.get(kind, [])))

    return reduce(_merge_config, list_all_extensions(), initial_value)


class Interactive(Extension):
    """Interactively choose and configure PyScaffold's parameters"""

    parser: ArgumentParser

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        setattr(self, CONFIG_KEY, {"ignore": [self.flag]})
        self.flags = [f"-{self.name[0].lower()}", self.flag]

    def augment_cli(self, parser: ArgumentParser):
        """See :obj:`~pyscaffold.extensions.Extension.augment_cli`."""
        self.parser = parser

        parser.add_argument(
            *self.flags,
            dest="command",
            action="store_const",
            const=self.command,
            help=self.help_text,
        )
        return self

    def command(self, opts: Opts):
        """This method replace the regular call to :obj:`cli.run_scaffold
        <pyscaffold.cli.run_scaffold>` with an intermediate file to confirm the user's
        choices in terms of arguments/options.
        """
        opts = expand_computed_opts(opts)
        examples = all_examples(self.parser, get_actions(self.parser), opts)
        content = (os.linesep * 2).join([HEADER.template, examples])
        with file_system.tmpfile(prefix="pyscaffold-", suffix=".args.sh") as file:
            file.write_text(content, "utf-8")
            content = shell.edit(file).read_text("utf-8")
            cli.main(split_args(content))  # Call the CLI again with the new options


def expand_computed_opts(opts: Opts) -> Opts:
    """Pre-process the given PyScaffold options and add default/computed values
    (including the ones derived from ``setup.cfg`` in case of ``--update`` or
    PyScaffold's own configuration file in the user's home directory.
    """
    _struct, opts = get_default_options({}, api.bootstrap_options(opts))
    return opts


def wrap(text: Optional[str], width=70, **kwargs) -> str:
    """Wrap text to fit lines with a maximum number of caracters"""
    return os.linesep.join(textwrap.wrap(text or "", width, **kwargs))


def comment(text: str, comment_mark="#", indent_level=0):
    """Comment each line of the given text (optionally indenting it)"""
    return textwrap.indent(text, (" " * indent_level) + comment_mark + " ")


def join_block(*parts: str, sep=os.linesep):
    """Join blocks of text using ``sep``, but ignoring the empty ones"""
    return sep.join(p for p in parts if p)


def long_option(action: Action):
    """Get the long option corresponding to the given :obj:`argparse.Action`"""
    return sorted(action.option_strings or [""], key=len)[-1]


def alternative_flags(action: Action):
    """Get the alternative flags (i.e. not the long one) of a :obj:`argparse.Action`"""
    flags = sorted(action.option_strings, key=len)[:-1]
    return f"(or alternatively: {' '.join(flags)})" if flags else ""


def has_active_extension(action: Action, opts: Opts) -> bool:
    """Returns :obj:`True` if the given :obj:`argparse.Action` corresponds to an
    extension that was previously activated via CLI.
    """
    ext_flags = [getattr(ext, "flag", None) for ext in opts.get("extensions", [])]
    return any(f in ext_flags for f in action.option_strings)


def example_no_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    """Generate a CLI example of option usage for a :obj:`argparse.Action` that do not
    expect arguments (``nargs = 0``).

    See :obj:`example`.
    """
    long = long_option(action)
    active_extension = has_active_extension(action, opts)
    value = opts.get(action.dest)
    stored_value = value == action.const and value != action.default
    # ^  This function is only invoked when `nargs == 0` (store_*)
    #    When the option is activated the value should be stored

    if long not in get_config("comment") and (active_extension or stored_value):
        return f" {long}"

    return comment(long)


def example_with_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    """Generate a CLI example of option usage for a :obj:`argparse.Action` that expects
    one or more arguments (``nargs`` is ``"?"``, ``"*"``, ``"+"`` or ``"N" > 0``).

    See :obj:`example`.
    """
    long = long_option(action)
    arg = opts.get(action.dest)

    if action.nargs in [None, 1, "?"]:
        value = shlex.quote(f"{arg}")
    elif isinstance(arg, (abc.Sequence, abc.Set)):
        # We are expecting a sequence/set since nargs is *, + or N > 1
        value = " ".join(shlex.quote(f"{a}") for a in arg).strip()
    else:
        value = ""

    if arg is None or long in get_config("comment") or value == "":
        return comment(f"{long} {format_args(parser, action)}".strip())

    return f" {long} {value}"


def example(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    """Generate a CLI example of option usage for the given :obj:`argparse.Action`.
    The ``opts`` argument corresponds to options already processed by PyScaffold, and
    interferes on the generated text (e.g., when the corresponding option is already
    processed, the example will be adjusted accordingly; when the
    corresponding option is not present, the example might be commented out; ...).

    This function will comment options that are marked in the ``"comment"``
    :obj:`configuration <CONFIG>`.
    """
    fn = example_no_value if action.nargs == 0 else example_with_value
    return fn(parser, action, opts)


def example_with_help(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    """Generate a CLI example of option usage for the given :obj:`argparse.Action` that
    includes a comment text block explaining its meaning (basically the same text
    displayed when using ``--help``).

    See :obj:`example`.
    """
    return join_block(
        example(parser, action, opts),
        comment(alternative_flags(action), indent_level=INDENT_LEVEL),
        comment(wrap(action.help), indent_level=INDENT_LEVEL),
    )


def all_examples(parser: ArgumentParser, actions: List[Action], opts: Opts) -> str:
    """Generate a example of usage of the CLI options corresponding to the given
    :obj:`actions <argparse.Action>` including the help text.

    This function will skip options that are marked in the ``"ignore"``
    :obj:`configuration <CONFIG>`.

    See :obj:`example_with_help`.
    """
    parts = (
        example_with_help(parser, a, opts)
        for a in actions
        if long_option(a) not in get_config("ignore")
    )
    return join_block(*parts, sep=os.linesep * 3)


def split_args(text: str) -> List[str]:
    """Split the text from the interactive example into arguments that can be passed
    directly to :mod:`argparse`, as if they were invoked directly from the CLI
    (this includes removing comments).
    """
    lines = (line.strip() for line in text.splitlines())
    return list(chain.from_iterable(shlex.split(x) for x in lines if x and x[0] != "#"))


# -- Functions that encapsulate calls to argparse non-public API --


def get_actions(parser: ArgumentParser):
    """List actions related to options that were configured to the given
    :obj:`ArgumentParser`.

    Warning:
        This function uses non-public API from Python's stdlib :mod:`argparse`.
    """
    return parser._actions


def format_args(parser: ArgumentParser, action: Action) -> str:
    """Produce an example to be used together with the flag of the given action.

    Warning:
        This function uses non-public API from Python's stdlib :mod:`argparse`.
    """
    formatter = parser._get_formatter()
    return formatter._format_args(action, action.dest)
