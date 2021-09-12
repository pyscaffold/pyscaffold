"""
Default PyScaffold's actions and functions to manipulate them.

When generating a project, PyScaffold uses a pipeline of functions (each function will
receive as arguments the values returned by the previous function). These functions
have an specific purpose and are called **actions**. Please follow the :obj:`Action`
signature when developing your own action.

Note:
    Some actions are more complex and are placed in dedicated modules together with
    other auxiliary functions, see :mod:`pyscaffold.structure`,
    :mod:`pyscaffold.update`.
"""
import os
from datetime import date, datetime
from functools import reduce
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Tuple

from . import info, repo
from .exceptions import (
    ActionNotFound,
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitDirtyWorkspace,
    InvalidIdentifier,
)
from .identification import (
    deterministic_name,
    deterministic_sort,
    get_id,
    is_valid_identifier,
    make_valid_identifier,
)
from .log import logger
from .structure import Structure, create_structure, define_structure
from .update import version_migration

if TYPE_CHECKING:  # pragma: no cover
    from .extensions import Extension  # avoid circular dependencies in runtime

ScaffoldOpts = Dict[str, Any]
"""Dictionary with PyScaffold's options, see :obj:`pyscaffold.api.create_project`."""

Action = Callable[[Structure, ScaffoldOpts], Tuple[Structure, ScaffoldOpts]]
"""Signature of a PyScaffold action, both arguments should be treated as immutable,
but a copy of the arguments, modified by the extension might be returned::

    Callable[[Structure, ScaffoldOpts], Tuple[Structure, ScaffoldOpts]]

"""

ActionParams = Tuple[Structure, ScaffoldOpts]
"""Both argument and return type of an action ``(struct, opts)``,
so a sequence of actions work in pipeline::

    Tuple[Structure, ScaffoldOpts]

When actions run, they can return an updated copy of :obj:`Structure` and
:obj:`ScaffoldOpts`.
"""


# -------- Functions that deal with/manipulate actions --------


def discover(extensions: Iterable["Extension"]) -> List[Action]:
    """Retrieve the action list.

    This is done by concatenating the default list with the one generated after
    activating the extensions.

    Args:
        extensions: list of functions responsible for activating the extensions.
    """
    actions = DEFAULT.copy()
    extensions = deterministic_sort(extensions)

    # Activate the extensions
    actions = reduce(_activate, extensions, actions)

    # Deduplicate actions
    return list({deterministic_name(a): a for a in actions}.values())


def invoke(struct_and_opts: ActionParams, action: Action) -> ActionParams:
    """Invoke action with proper logging.

    Args:
        struct_and_opts: PyScaffold's arguments for actions
        action: to be invoked

    Returns:
        ActionParams: updated project representation and options
    """
    logger.report("invoke", get_id(action))
    with logger.indent():
        return action(*struct_and_opts)


def register(
    actions: List[Action],
    action: Action,
    before: Optional[str] = None,
    after: Optional[str] = None,
) -> List[Action]:
    """Register a new action to be performed during scaffold.

    Args:
        actions (List[Action]): previous action list.
        action (Action): function with two arguments: the first one is a
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

                register(actions, do_nothing,
                         after='create_structure')
                    # Look for the first action with a name
                    # `create_structure` and inserts `do_nothing` after it.
                    # If more than one registered action is named
                    # `create_structure`, the first one is selected.

                register(
                    actions, do_nothing,
                    before='pyscaffold.structure:create_structure')
                    # Similar to the previous example, but the probability
                    # of name conflict is decreased by including the module
                    # name.

            When no keyword argument is provided, the default execution
            order specifies that the action will be performed after the
            project structure is defined, but before it is written to the
            disk. Example::

                register(actions, do_nothing)
                    # The action will take place after
                    # `pyscaffold.structure:define_structure`

    Returns:
        List[Action]: modified action list.
    """
    reference = before or after or get_id(define_structure)
    position = _find(actions, reference)
    if not before:
        position += 1

    clone = actions[:]
    clone.insert(position, action)

    return clone


def unregister(actions: List[Action], reference: str) -> List[Action]:
    """Prevent a specific action to be executed during scaffold.

    Args:
        actions (List[Action]): previous action list.
        reference (str): action identifier. Similarly to the keyword
            arguments of :obj:`register` it can assume two formats:

                - the name of the function alone,
                - the name of the module followed by ``:`` and the name
                  of the function

    Returns:
        List[Action]: modified action list.
    """
    position = _find(actions, reference)
    return actions[:position] + actions[position + 1 :]


def _find(actions: Iterable[Action], name: str) -> int:
    """Find index of name in actions"""
    if ":" in name:
        names = [get_id(action) for action in actions]
    else:
        names = [action.__name__ for action in actions]

    try:
        return names.index(name)
    except ValueError:
        raise ActionNotFound(name)


# -------- PyScaffold's actions --------


def get_default_options(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Compute all the options that can be automatically derived.

    This function uses all the available information to generate sensible
    defaults. Several options that can be derived are computed when possible.

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        ActionParams: project representation and options with default values set

    Raises:
        :class:`~.DirectoryDoesNotExist`: when PyScaffold is told to
            update an nonexistent directory
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information

    Note:
        This function uses git to determine some options, such as author name
        and email.
    """
    # This function uses information from git, so make sure it is available
    info.check_git()

    project_path = str(opts.get("project_path", ".")).rstrip(os.sep)
    # ^  Strip (back)slash when added accidentally during update
    opts["project_path"] = Path(project_path)
    opts.setdefault("name", opts["project_path"].resolve().name)
    opts.setdefault("package", make_valid_identifier(opts["name"]))
    opts.setdefault("author", info.username())
    opts.setdefault("email", info.email())
    opts.setdefault("description", "")
    opts.setdefault("url", "")
    opts.setdefault("release_date", date.today().strftime("%Y-%m-%d"))
    # All kinds of derived parameters
    year = datetime.strptime(opts["release_date"], "%Y-%m-%d").year
    opts.setdefault("year", year)
    opts.setdefault(
        "title",
        "=" * len(opts["name"]) + "\n" + opts["name"] + "\n" + "=" * len(opts["name"]),
    )
    opts.setdefault("isolated_build", opts.setdefault("pyproject", True))

    # Initialize empty list of all requirements and extensions
    # (since not using deep_copy for the DEFAULT_OPTIONS, better add compound
    # values inside this function)
    opts.setdefault("requirements", [])
    opts.setdefault("extensions", [])
    opts.setdefault("root_pkg", opts["package"])
    opts.setdefault("qual_pkg", opts["package"])
    opts.setdefault("pretend", False)

    opts["license"] = info.best_fit_license(opts.get("license"))
    # ^ "Canonicalise" license

    return struct, opts


def verify_options_consistency(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Perform some sanity checks about the given options.

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        Updated project representation and options
    """
    if not is_valid_identifier(opts["package"]):
        raise InvalidIdentifier(
            f"Package name {opts['package']!r} is not a valid identifier."
        )

    if opts["update"] and not opts["force"]:
        if not info.is_git_workspace_clean(opts["project_path"]):
            raise GitDirtyWorkspace

    return struct, opts


def verify_project_dir(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Check if PyScaffold can materialize the project dir structure.

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        Updated project representation and options
    """
    if opts["project_path"].exists():
        if not opts["update"] and not opts["force"]:
            raise DirectoryAlreadyExists(
                "Directory {dir} already exists! Use the `update` option to "
                "update an existing project or the `force` option to "
                "overwrite an existing directory.".format(dir=opts["project_path"])
            )
    elif opts["update"]:
        raise DirectoryDoesNotExist(
            "Project {path} does not exist and thus cannot be "
            "updated!".format(path=opts["project_path"])
        )

    return struct, opts


def init_git(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add revision control to the generated files.

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        Updated project representation and options
    """
    path = opts.get("project_path", ".")
    if not opts["update"] and not repo.is_git_repo(path):
        repo.init_commit_repo(path, struct, log=True, pretend=opts.get("pretend"))

    return struct, opts


def report_done(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Just inform the user PyScaffold is done"""
    try:
        print("done! 🐍 🌟 ✨")
    except Exception:  # pragma: no cover
        print("done!")  # this exception is not really expected to happen
    return struct, opts


DEFAULT: List[Action] = [
    get_default_options,
    verify_options_consistency,
    define_structure,
    verify_project_dir,
    version_migration,
    create_structure,
    init_git,
    report_done,
]
"""Default list of actions forming the main pipeline executed by PyScaffold"""


# -------- Auxiliary functions --------


def _activate(actions: List[Action], extension: "Extension") -> List[Action]:
    """Activate extension with proper logging.
    The order of args is inverted to facilitate ``reduce``
    """
    logger.report("activate", extension.__module__)
    with logger.indent():
        return extension(actions)
