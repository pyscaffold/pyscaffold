"""
Parser for the Command-Line-Interface of PyScaffold

The main idea is to use Python's :obj:`argparse.ArgumentParser` and extend it:
 * to support `noprompt` in `add_argument` if an argument should never be prompted for
 * to track easily which command line options of all possible ones were specified
   and prompt only for the remaining ones if `nopromot` = False

Since the authors of ArgumentParser did *NOT* favor Composition over Inheritance
a lot of MixedIns had to be used.
"""

from argparse import Action
from argparse import ArgumentParser as OriginalParser
from functools import reduce
from typing import Any, Callable, Dict, List, Union

import inquirer

from .actions import ScaffoldOpts
from .extensions import Extension

PromptFn = Callable[["ArgumentParser", Action, ScaffoldOpts], ScaffoldOpts]
PromptMap = Dict[Action, Union[bool, PromptFn]]
# ^  TODO: Use Literal[False] instead of bool when `python_requires = >= 3.8`


ARGUMENT_MSG = "Arguments of [{}] (enter for default)"
ACTIVATE_MSG = "Activate"
CHOICES_MSG = "Choices"
INCOMPAT_MSG = "argparse {} is incompatible with PyScaffold's interactive mode"


def default_prompt(
    parser: "ArgumentParser",
    action: Action,
    opts: ScaffoldOpts,
) -> ScaffoldOpts:
    """Interacts with user to obtain values for the given :obj:`Action`"""
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

    return merge_user_input(opts, input, action)


class ArgumentParser(OriginalParser):
    """Extends ArgumentParser to allow any interactive prompts"""

    def __init__(self, *args, **kwargs):
        self._action_prompt: PromptMap = {}
        self.orig_args: List[str] = []
        super().__init__(*args, **kwargs)

    def add_argument_group(self, *args, **kwargs):
        raise NotImplementedError(INCOMPAT_MSG.format("add_argument_group"))

    def add_mutually_exclusive_group(self, *args, **kwargs):
        raise NotImplementedError(INCOMPAT_MSG.format("add_mutually_exclusive_group"))

    def add_argument(
        self, *args, prompt: Union[bool, PromptFn] = default_prompt, **kwargs
    ) -> Action:
        """Adds `prompt` to the kwargs of obj:`argparse.ArgumentParser`.

        By default :obj:`default_prompt` is used in interactive mode, but
        when `prompt` is False, PyScaffold will skip the option. A custom
        :obj:`PromptFn` callable can also be passed.
        """
        action = super().add_argument(*args, **kwargs)
        self._action_prompt[action] = prompt
        return action

    def parse_args(self, args=None, namespace=None):
        self.orig_args = args[:]
        return super().parse_args(args, namespace)

    def was_action_called(self, action):
        return any(s in self.orig_args for s in action.option_strings)

    def _filter_prompts(self, extensions: List[Extension]) -> Dict[Action, PromptFn]:
        return {
            action: prompt
            for action, prompt in self._action_prompt.items()
            if (
                callable(prompt)
                and not self.was_action_called(action)
                and not is_included(action, extensions)
            )
        }

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
        prompts = self._filter_prompts(opts["extensions"])  # maps Action to PromptFn
        return reduce(lambda opts, act: prompts[act](self, act, opts), prompts, opts)


def is_included(action: Action, extensions: List[Extension]):
    """Checks if action was included by another extension.

    An extension can include another using :obj:`~pyscaffold.extensions.include`
    """
    ext_flags = [ext.flag for ext in extensions]
    return any(f in ext_flags for f in action.option_strings)


def merge_user_input(opts: ScaffoldOpts, input: Any, action: Action) -> ScaffoldOpts:
    # ToDo: use the parser of action to parse the user's input
    if action.dest == "extensions":
        return {**opts, "extensions": opts["extensions"] + action.const}

    return {**opts, action.dest: input}
