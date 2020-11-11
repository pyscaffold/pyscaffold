"""Extension that generates configuration for Cirrus CI."""
import os
import textwrap
from argparse import Action, ArgumentParser
from typing import List, Optional

from ..actions import ScaffoldOpts as Opts
from . import Extension

INDENT_LEVEL = 4
SKIP = ["help"]


class Edit(Extension):
    """Add configuration file for Cirrus CI (includes `--pre-commit`)"""

    parser: ArgumentParser

    def augment_cli(self, parser: ArgumentParser):
        """Augments the command-line interface parser.
        See :obj:`~pyscaffold.extension.Extension.augment_cli`.
        """
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
        """This method replace the regular call to PyScaffold with some intermediate
        steps:

        1. First it uses the already parsed arguments (first pass) to generate an
           ``arguments file`` (in a similar fashion the popular program Astyle uses
           ``.astylerc`` files)
        2. Let the user edit the file
        3. When the user close the file it parses its contents again,
           using the same CLI methods
        4. Finally putup is called again with contents of the given file
        """
        # file = self.generate_file(opts)
        # if not edit(file): error
        # new_opts = cli.parse_args(args_from_file)
        # return cli.run_scaffold(new_opts)


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
    option_line = long_option(action)
    if opts.get(action.dest) or has_active_extension(action, opts):
        return option_line

    return comment(option_line)


def example_with_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    long = long_option(action)

    arg = opts.get(action.dest)
    if arg is None:
        formatter = parser._get_formatter()
        return comment(f"{long} {formatter._format_args(action, action.dest)}".strip())

    args = arg if isinstance(arg, (list, tuple)) else [arg]
    return (long_option(action) + " " + " ".join(f"{a}" for a in args)).strip()


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
    parts = (example_with_help(parser, a, opts) for a in actions if a.dest not in SKIP)
    return join_block(*parts, sep=os.linesep * 3)
