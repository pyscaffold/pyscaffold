"""Similarly to ``git rebase -i`` this extension allows users to interactively
choose with options apply to ``putup``, by editing a file filled with examples.

Warning:

    Due to the way :mod:`argparse` is written, it is not very easy to obtain information
    about what are the options and arguments a given parse is currently configured with.
    There are no public methods that allow inspection, and therefore in order to do so,
    one has to rely in a few non-public methods (according to Python's convention, the
    ones starting with a ``_`` symbol).
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
from . import Extension, iterate_entry_points

INDENT_LEVEL = 4
HEADER = templates.get_template("header_edit")


CONFIG = {
    "ignore": ["--help", "--version"],
    "comment": ["--verbose", "--very-verbose"],
}
"""Configuration for the options that are not associated with an extension class.

This dict is used by the :obj:`get_config` function, and will be augmented
by each extension via the ``on_edit`` attribute.
"""


@lru_cache(maxsize=2)
def get_config(kind: str) -> Set[str]:
    """Get configurations that will be used for generating examples.

    The ``kind`` argument can assume 2 values, and will result in a different output:

    - ``"ignore"``: Options that should be simply ignored when creating examples
    - ``"comment"``: Options that should be commented when creating examples,
        even if they appear in the original ``sys.argv``.
    """
    # TODO: when `python_requires >= 3.8` use Literal["ignore", "comment"] instead of
    #       str for type annotation of kind
    assert kind in CONFIG.keys()
    initial_value = set(CONFIG[kind])

    def _reducer(acc, ext):
        config_from_ext = getattr(ext, "on_edit", {"ignore": [], "comment": []})
        return acc | set(config_from_ext.get(kind, []))

    return reduce(_reducer, iterate_entry_points(), initial_value)


class Edit(Extension):
    """Allows to user to choose PyScaffold's options by editing a file with examples."""

    parser: ArgumentParser
    on_edit = {"ignore": ["--edit"]}

    def augment_cli(self, parser: ArgumentParser):
        """See :obj:`~pyscaffold.extension.Extension.augment_cli`."""
        self.parser = parser

        parser.add_argument(
            self.flag,
            dest="command",
            action="store_const",
            const=self.command,
            help=self.help_text,
        )
        return self

    def command(self, opts: Opts):
        """This method replace the regular call to :obj:`cli.run_scaffold` with an
        intermediate file to confirm the user's choices in terms of arguments/options.
        """
        opts = expand_computed_opts(opts)
        examples = all_examples(self.parser, get_actions(self.parser), opts)
        content = (os.linesep * 2).join([HEADER.template, examples])
        with file_system.tmpfile(prefix="pyscaffold-", suffix=".args.sh") as file:
            file.write_text(content, "utf-8")
            content = shell.edit(file).read_text("utf-8")
            cli.main(split_args(content))  # Call the CLI again with the new options


def expand_computed_opts(opts: Opts) -> Opts:
    _struct, opts = get_default_options({}, api.bootstrap_options(opts))
    return opts


def wrap(text: Optional[str], width=70, **kwargs) -> str:
    return os.linesep.join(textwrap.wrap(text or "", width, **kwargs))


def comment(text: str, comment_mark="#", indent_level=0):
    return textwrap.indent(text, (" " * indent_level) + comment_mark + " ")


def join_block(*parts: str, sep=os.linesep):
    return sep.join(p for p in parts if p)


def long_option(action: Action):
    return sorted(action.option_strings or [""], key=len)[-1]


def alternative_flags(action: Action):
    opts = sorted(action.option_strings, key=len)[:-1]
    return f"(or alternatively: {' '.join(opts)})" if opts else ""


def has_active_extension(action: Action, opts: Opts) -> bool:
    ext_flags = [getattr(ext, "flag", None) for ext in opts.get("extensions", [])]
    return any(f in ext_flags for f in action.option_strings)


def example_no_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    long = long_option(action)
    active_extension = has_active_extension(action, opts)
    value = opts.get(action.dest)
    stored_value = (value in [action.const, True, False]) and (value is not None)
    # ^  This function is only invoked when `nargs == 0` (store_true, store_false or
    #    store_const). When the option is activated the value should be stored

    if long not in get_config("comment") and (active_extension or stored_value):
        return f" {long}"

    return comment(long)


def example_with_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
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
    fn = example_no_value if action.nargs == 0 else example_with_value
    return fn(parser, action, opts)


def example_with_help(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    return join_block(
        example(parser, action, opts),
        comment(alternative_flags(action), indent_level=INDENT_LEVEL),
        comment(wrap(action.help), indent_level=INDENT_LEVEL),
    )


def all_examples(parser: ArgumentParser, actions: List[Action], opts: Opts) -> str:
    parts = (
        example_with_help(parser, a, opts)
        for a in actions
        if long_option(a) not in get_config("ignore")
    )
    return join_block(*parts, sep=os.linesep * 3)


def split_args(text: str) -> List[str]:
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
