"""
Parser for the Command-Line-Interface of PyScaffold

The main idea is to use Python's :obj:`argparse.ArgumentParser` and extend it:
 * to support `noprompt` in `add_argument` if an argument should never be prompted for
 * to track easily which command line options of all possible ones were specified
   and prompt only for the remaining ones if `nopromot` = False

Since the authors of ArgumentParser did *NOT* favor Composition over Inheritance
a lot of MixedIns had to be used.
"""

import sys
from argparse import Action, ArgumentParser, _ArgumentGroup, _MutuallyExclusiveGroup
from typing import List, Set

import inquirer

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

from .actions import ScaffoldOpts
from .extensions import Extension


class GroupMixin(object):
    """Adds some more references to the container for group classes"""

    def __init__(self, container, *args, **kwargs):
        # link to container objects like in argparse
        self.actions = container.actions
        self.noprompts = container.noprompts
        self.called_actions = container.called_actions
        super().__init__(container, *args, **kwargs)


class AddActionMixin(object):
    """Wraps action to log it when called"""

    def _add_action(self, action: Action) -> Action:
        if not isinstance(action, ActionWrapper):
            self.actions.append(action)
            action = ActionWrapper(action, self.called_actions)
        return super()._add_action(action)


class AddArgumentMixin(object):
    def add_argument(self, *args, noprompt: bool = False, **kwargs) -> Action:
        """
        For all unlisted arguments, refer to the parent class
        Args:
            noprompt: don't prompt the user in interactive mode
        """
        action = super().add_argument(*args, **kwargs)
        # store if action is not meant for prompting
        if noprompt:
            self.noprompts.add(self.actions[-1])  # store unwrapped action
        return action


class _MutuallyExclusiveGroup(
    GroupMixin, AddActionMixin, AddArgumentMixin, _MutuallyExclusiveGroup
):
    pass


class _ArgumentGroup(GroupMixin, AddActionMixin, AddArgumentMixin, _ArgumentGroup):
    pass


class ActionWrapper(Action):
    def __init__(self, action: Action, called_actions: List[Action]):
        self._action = action
        self._called_actions = called_actions
        super().__init__(**dict(action._get_kwargs()))
        # transfer missing attributes since not all are listed in _get_kwargs
        for attr in [attr for attr in dir(self) if not attr.startswith("_")]:
            setattr(self, attr, getattr(action, attr))

    def __call__(self, *args, **kwargs):
        self._action(*args, **kwargs)
        self._called_actions.append(self._action)


class ArgumentParser(AddArgumentMixin, ArgumentParser):
    """
    Extends ArgumentParser to allow any unspecified arguments
    """

    def __init__(self, *args, **kwargs):
        self.actions: List[Action] = []  # original, unwrapped actions
        self.called_actions: List[Action] = []
        self.noprompts: Set[Action] = set()
        super().__init__(*args, **kwargs)

    def add_argument_group(self, *args, **kwargs) -> _ArgumentGroup:
        group = _ArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        return group

    def add_mutually_exclusive_group(self, **kwargs) -> _MutuallyExclusiveGroup:
        group = _MutuallyExclusiveGroup(self, **kwargs)
        self._mutually_exclusive_groups.append(group)
        return group

    def _get_prompt_actions(self, extensions: List[Extension]) -> List[Action]:
        prompt_actions = []
        for action in self.actions:
            if action in self.noprompts:
                continue
            if action.dest == "help":
                continue
            if action in self.called_actions:
                continue
            # check if action was included by another, e.g. cirrus -> pre-commit
            if is_included(action, extensions):
                continue
            prompt_actions.append(action)

        return prompt_actions

    def prompt_user(self, opts: ScaffoldOpts) -> ScaffoldOpts:
        """Prompt the user for additional options

        ToDo: Avoid cutting the message if terminal is too small, rather wrap
         This seems to be a problem with inquiry.
        ToDo: Give a nice error message if user cancels the prompting with ctrl+c
        ToDo: Show the user the defaults from `actions.get_default_options` by
         extracting this functionality into smaller functions that can be applied here
        """
        questions = []
        for action in self._get_prompt_actions(opts["extensions"]):
            name = _get_action_key(action)
            flag = action.option_strings[-1]
            message = f"flag: {flag}, help: {action.help}"
            if action.nargs == 0:
                question = inquirer.Confirm(name, message=message, default=False)
            elif action.nargs == "?":
                # ToDo: Handle here nicely somehow between not using (default: None)
                #       and using with a default or using with a custom value
                #       This is necessary for extensions like --venv
                question = inquirer.Text(name, message, default=None)
            elif action.choices:
                question = inquirer.List(name, message, choices=action.choices)
            else:
                question = inquirer.Text(name, message, default=None)
            questions.append(question)
        result = inquirer.prompt(questions)

        # ToDo: This needs to be nicer, not just copy&paste from cli.py
        extensions = {
            extension.name: extension.load()(extension.name)
            for extension in entry_points().get("pyscaffold.cli", [])
        }
        add_ext_names = [q for q, a in result.items() if a and q in extensions]
        opts["extensions"].extend([extensions[name] for name in add_ext_names])
        # use the remaining answers of the user to update the parameter options
        result = {q: a for q, a in result.items() if q not in add_ext_names}
        return {**opts, **result}


def _get_action_key(action: Action) -> str:
    # ToDo: This is quite error-prone, the string "extensions" should be
    #  defined as CONSTANT somewhere
    if action.dest == "extensions":
        return action.const.name
    else:
        return action.dest


def is_included(action: Action, extensions: List[Extension]):
    """Checks if action was included by another extension

    An extension can include another using :obj:`~pyscaffold.extensions.include`
    """
    return getattr(action, "const", "NOT_INCLUDED") in extensions
