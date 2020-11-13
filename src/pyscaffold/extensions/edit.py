import os
import shlex
import textwrap
from argparse import Action, ArgumentParser
from itertools import chain
from typing import List, Optional

from .. import api, cli, file_system, shell, templates
from ..actions import ScaffoldOpts as Opts
from ..actions import get_default_options
from . import Extension

INDENT_LEVEL = 4
SKIP = ["--help", "--edit"]
COMMENT = ["--version", "--verbose", "--very-verbose", "--no-config"]
HEADER = templates.get_template("header_edit")


class Edit(Extension):
    """Allows to user to choose PyScaffold's options by editing a file with examples."""

    parser: ArgumentParser

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
        examples = all_examples(self.parser, self.parser._actions, opts)
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
    if (
        long not in COMMENT
        and (action.dest != "extensions" and opts.get(action.dest))
        or has_active_extension(action, opts)
    ):
        return f" {long}"

    return comment(long)


def example_with_value(parser: ArgumentParser, action: Action, opts: Opts) -> str:
    long = long_option(action)

    arg = opts.get(action.dest)
    if arg is None or long in COMMENT:
        formatter = parser._get_formatter()
        return comment(f"{long} {formatter._format_args(action, action.dest)}".strip())

    args = arg if isinstance(arg, (list, tuple)) else [arg]
    return (f" {long} " + " ".join(shlex.quote(f"{a}") for a in args)).rstrip()


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
        if long_option(a) not in SKIP
    )
    return join_block(*parts, sep=os.linesep * 3)


def split_args(text: str) -> List[str]:
    lines = (line.strip() for line in text.splitlines())
    return list(chain.from_iterable(shlex.split(x) for x in lines if x and x[0] != "#"))
