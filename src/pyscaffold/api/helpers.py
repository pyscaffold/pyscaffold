"""
Useful functions for manipulating the action list and project structure.
"""

from ..exceptions import ActionNotFound
from ..identification import get_id
from ..log import logger
from ..structure import define_structure

logger = logger  # Sphinx workaround to force documenting imported members
"""Logger wrapper, that provides methods like :obj:`~.ReportLogger.report`.
See :class:`~.ReportLogger`.
"""


# -------- Action List --------


def register(actions, action, before=None, after=None):
    """Register a new action to be performed during scaffold.

    Args:
        actions (list): previous action list.
        action (callable): function with two arguments: the first one is a
            (nested) dict representing the file structure of the project
            and the second is a dict with scaffold options.
            This function **MUST** return a tuple with two elements similar
            to its arguments. Example::

                def do_nothing(struct, opts):
                    return (struct, opts)

        **kwargs (dict): keyword arguments make it possible to choose a
            specific order when executing actions: when ``before`` or
            ``after`` keywords are provided, the argument value is used as
            a reference position for the new action. Example::

                helpers.register(actions, do_nothing,
                                 after='create_structure')
                    # Look for the first action with a name
                    # `create_structure` and inserts `do_nothing` after it.
                    # If more than one registered action is named
                    # `create_structure`, the first one is selected.

                helpers.register(
                    actions, do_nothing,
                    before='pyscaffold.structure:create_structure')
                    # Similar to the previous example, but the probability
                    # of name conflict is decreased by including the module
                    # name.

            When no keyword argument is provided, the default execution
            order specifies that the action will be performed after the
            project structure is defined, but before it is written to the
            disk. Example::


                helpers.register(actions, do_nothing)
                    # The action will take place after
                    # `pyscaffold.structure:define_structure`

    Returns:
        list: modified action list.
    """
    reference = before or after or get_id(define_structure)
    position = _find(actions, reference)
    if not before:
        position += 1

    clone = actions[:]
    clone.insert(position, action)

    return clone


def unregister(actions, reference):
    """Prevent a specific action to be executed during scaffold.

    Args:
        actions (list): previous action list.
        reference (str): action identifier. Similarly to the keyword
            arguments of :obj:`~.register` it can assume two formats:

                - the name of the function alone,
                - the name of the module followed by ``:`` and the name
                  of the function

    Returns:
        list: modified action list.
    """
    position = _find(actions, reference)
    return actions[:position] + actions[position + 1 :]


def _find(actions, name):
    """Find index of name in actions"""
    if ":" in name:
        names = [get_id(action) for action in actions]
    else:
        names = [action.__name__ for action in actions]

    try:
        return names.index(name)
    except ValueError:
        raise ActionNotFound(name)
