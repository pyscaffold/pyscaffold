"""
Parser for the Command-Line-Interface of PyScaffold

The main idea is to use Python's :obj:`argparse.ArgumentParser` and extend it:
 * to support `prompt` in `add_argument` if an argument should be prompted for
 * to track easily which command line options of all possible ones were specified
   and prompt only for the remaining ones if `prompt` = True
"""

from argparse import Action
from argparse import ArgumentParser as OriginalParser
from argparse import Namespace
from functools import partial, reduce
from typing import Any, Callable, Dict, Iterator, List, Tuple, Union

import inquirer

from .actions import ScaffoldOpts
from .extensions import Extension

PartialPrompt = Callable[[ScaffoldOpts], ScaffoldOpts]
PromptFn = Callable[["ArgumentParser", Action, ScaffoldOpts], ScaffoldOpts]
Prompt = Union[bool, PromptFn]
# ^  TODO: Use Literal[False] instead of bool when `python_requires = >= 3.8`
PromptMap = Dict[Action, Prompt]
ArgMap = Dict[Action, Tuple[Union[list, tuple], dict]]


ARGUMENT_MSG = "Arguments of [{}] (enter for default)"
ACTIVATE_MSG = "Activate"
CHOICES_MSG = "Choices"


def default_prompt(
    parser: "ArgumentParser", action: Action, opts: ScaffoldOpts
) -> ScaffoldOpts:
    """Interacts with user to obtain values for the given :obj:`Action`.

    This function is responsible for printing an "interactive question" in the terminal,
    waiting for the user input and parsing the given input.
    It should return a modified version of ``opts`` with added values corresponding
    to the given CLI argument (relative to ``action``).
    """
    if is_included(action, opts["extensions"]):
        print(f"{action.dest} included via extensions {opts['extensions']!r}")
        return opts

    flag = parser.format_flag(action)
    print("Flag:", flag)
    print("Help:", action.help)

    if action.nargs == 0:
        input = inquirer.confirm(ACTIVATE_MSG, default=False)
    elif action.nargs == "?":
        input = inquirer.confirm(ACTIVATE_MSG, default=False)
        if input:
            input = inquirer.text(ARGUMENT_MSG.format(flag), default=action.default)
        else:
            input = None
    elif action.choices:
        input = inquirer.list_input(CHOICES_MSG, choices=action.choices)
    else:
        input = inquirer.text(ARGUMENT_MSG.format(flag), default=None)

    return parser.merge_user_input(opts, input, action)


class ArgumentParser(OriginalParser):
    """Extends ArgumentParser to allow any interactive prompts.

    .. warning:: ``add_mutually_exclusive_group``, ``add_argument_group`` and
        ``add_subparsers`` are not supported in PyScaffold's interactive mode.
    """

    def __init__(self, *args, **kwargs):
        self.hidden = ["help"]
        self._action_prompt: PromptMap = {}
        self._added_arguments: ArgMap = {}
        self.orig_args: List[str] = []
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, prompt: Prompt = default_prompt, **kwargs) -> Action:
        """Similar to obj:`argparse.ArgumentParser.add_argument, but with an extra
        ``prompt`` keyword argument.

        By default :obj:`default_prompt` is used to ask the user in interactive mode,
        unless `prompt=False`. A custom :obj:`PromptFn` callable can also be passed.
        """
        action = super().add_argument(*args, **kwargs)
        if action.option_strings:
            self._action_prompt[action] = prompt
        self._added_arguments[action] = (args, kwargs)
        return action

    def parse_args(self, args=None, namespace=None):
        self.orig_args = args[:]
        return super().parse_args(args, namespace)

    def was_action_called(self, action):
        return any(s in self.orig_args for s in action.option_strings)

    def _filter_prompts(self, extensions: List[Extension]) -> Iterator[PartialPrompt]:
        return (
            partial(prompt, self, action)
            for action, prompt in self._action_prompt.items()
            if (
                callable(prompt)
                and action.dest not in self.hidden
                and not self.was_action_called(action)
                and not is_included(action, extensions)
            )
        )

    def format_flag(self, action: Action) -> str:
        flag = action.option_strings[-1]
        formatter = self._get_formatter()
        args = formatter._format_args(action, action.dest)
        return f"{flag} {args}"

    def prompt_user(self, opts: ScaffoldOpts) -> ScaffoldOpts:
        """Prompt the user for additional options

        ToDo: Give a nice error message if user cancels the prompting with ctrl+c
        ToDo: Show the user the defaults from `actions.get_default_options` by
         extracting this functionality into smaller functions that can be applied here
        """
        prompts = self._filter_prompts(opts["extensions"])
        return reduce(lambda acc, question: question(acc), prompts, opts)

    def merge_user_input(
        self, opts: ScaffoldOpts, input: Any, action: Action
    ) -> ScaffoldOpts:
        """Parse user input and augment the existing options with the corresponding
        values.
        """
        # Create a temporary parse to parse a single option corresponding to `action`
        tmp_parser = OriginalParser()
        args, kwargs = self._added_arguments[action]
        tmp_parser.add_argument(*args, **kwargs)
        namespace = Namespace(**opts)

        # Recreate a "simplified equivalent" of the CLI args for the single option
        flag = action.option_strings[-1]
        if input is False:
            cli_args = []
        elif input in [None, True]:
            cli_args = [flag]
        elif isinstance(input, (list, tuple)):
            cli_args = [flag, *[str(x) for x in input]]
        else:
            cli_args = [flag, str(input)]

        return vars(tmp_parser.parse_args(cli_args, namespace=namespace))


def is_included(action: Action, extensions: List[Extension]):
    """Checks if action was included by another extension.

    An extension can include another using :obj:`~pyscaffold.extensions.include`
    """
    ext_flags = [ext.flag for ext in extensions]
    return any(f in ext_flags for f in action.option_strings)
