# -*- coding: utf-8 -*-
"""
Exposed API for accessing PyScaffold via Python.

In addition to the functions and classes exposed in this module, please also
consider :obj:`pyscaffold.templates.get_template` to be part of PyScaffold's
public API.
"""
import os
from datetime import date, datetime
from enum import Enum
from functools import reduce
from pathlib import Path

import pyscaffold

from .. import info, repo, utils
from ..exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitDirtyWorkspace,
    InvalidIdentifier,
    NoPyScaffoldProject,
)
from ..log import logger
from ..structure import create_structure, define_structure
from ..update import invoke_action, version_migration
from . import helpers

# -------- Extension Main Class --------


class Extension(object):
    """Base class for PyScaffold's extensions

    Args:
        name (str): How the extension should be named. Default: name of class
            By default, this value is used to create the activation flag in
            PyScaffold cli.
    """

    mutually_exclusive = False

    def __init__(self, name):
        self.name = name
        self.args = None

    @property
    def flag(self):
        return "--{flag}".format(flag=utils.dasherize(self.name))

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
        """Shortcut for :obj:`helpers.register`"""
        return helpers.register(*args, **kwargs)

    @staticmethod
    def unregister(*args, **kwargs):
        """Shortcut for :obj:`helpers.unregister`"""
        return helpers.unregister(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Just delegating to :obj:`self.activate`"""
        return self.activate(*args, **kwargs)


# -------- Options --------

(NO_CONFIG,) = list(Enum("ConfigFiles", "NO_CONFIG"))
"""This constant is used to tell PyScaffold to not load any extra configuration file,
not even the default ones
Usage::

    create_project(opts, config_files=NO_CONFIG)

Please notice that the ``setup.cfg`` file inside an project being updated will
still be considered.
"""

DEFAULT_OPTIONS = {
    "update": False,
    "force": False,
    "description": "Add a short description here!",
    "url": "https://github.com/pyscaffold/pyscaffold/",
    "license": "mit",
    "version": pyscaffold.__version__,
    "classifiers": ["Development Status :: 4 - Beta", "Programming Language :: Python"],
    "extensions": [],
    "config_files": [],  # Overloaded in bootstrap_options for lazy evaluation
}


def bootstrap_options(opts=None, **kwargs):
    """Augument the given options with minimal defaults
    and existing configurations saved in files (e.g. ``setup.cfg``)

    See list of arguments in :func:`create_project`.
    Returns a dictionary of options.

    Note:
        This function does not replace the :func:`get_default_options`
        action. Instead it is needed to ensure that action works correctly.
    """
    opts = opts if opts else {}
    opts.update(kwargs)
    given_opts = opts

    # Defaults:
    opts = DEFAULT_OPTIONS.copy()
    default_files = [info.config_file(default=None)]
    opts["config_files"] = [f for f in default_files if f and f.exists()]
    # ^ make sure the file exists before passing it ahead

    opts.update({k: v for k, v in given_opts.items() if v or v is False})
    # ^  Remove empty items, so we ensure setdefault works

    return _read_existing_config(opts)
    # ^  Add options stored in config files


# -------- Actions --------


def discover_actions(extensions):
    """Retrieve the action list.

    This is done by concatenating the default list with the one generated after
    activating the extensions.

    Args:
        extensions (list): list of functions responsible for activating the
        extensions.

    Returns:
        list: scaffold actions.
    """
    actions = DEFAULT_ACTIONS.copy()

    # Remove duplicates and order the extensions lexicographically which is
    # needed for determinism, also internal before external
    # "pyscaffold.*" < "pyscaffoldext.*"
    def qual_name(ext):
        return ".".join([ext.__module__, ext.__class__.__qualname__])

    deduplicated = {qual_name(e): e for e in extensions}
    extensions = [v for (_k, v) in sorted(deduplicated.items())]

    # Activate the extensions
    return reduce(lambda acc, f: _activate(f, acc), extensions, actions)


def get_default_options(struct, opts):
    """Compute all the options that can be automatically derived.

    This function uses all the available information to generate sensible
    defaults. Several options that can be derived are computed when possible.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        dict, dict: project representation and options with default values set

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
    opts.setdefault("name", opts["project_path"].name)
    opts.setdefault("package", utils.make_valid_identifier(opts["name"]))
    opts.setdefault("author", info.username())
    opts.setdefault("email", info.email())
    opts.setdefault("release_date", date.today().strftime("%Y-%m-%d"))
    # All kinds of derived parameters
    year = datetime.strptime(opts["release_date"], "%Y-%m-%d").year
    opts.setdefault("year", year)
    opts.setdefault(
        "title",
        "=" * len(opts["name"]) + "\n" + opts["name"] + "\n" + "=" * len(opts["name"]),
    )

    # Initialize empty list of all requirements and extensions
    # (since not using deep_copy for the DEFAULT_OPTIONS, better add compound
    # values inside this function)
    opts.setdefault("requirements", list())
    opts.setdefault("extensions", list())
    opts.setdefault("root_pkg", opts["package"])
    opts.setdefault("qual_pkg", opts["package"])
    opts.setdefault("pretend", False)

    # Save cli params for later updating
    extensions = set(opts.get("cli_params", {}).get("extensions", []))
    args = opts.get("cli_params", {}).get("args", {})
    for extension in opts["extensions"]:
        extensions.add(extension.name)
        if extension.args is not None:
            args[extension.name] = extension.args
    opts["cli_params"] = {"extensions": list(extensions), "args": args}

    return struct, opts


def verify_options_consistency(struct, opts):
    """Perform some sanity checks about the given options.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        dict, dict: updated project representation and options
    """
    if not utils.is_valid_identifier(opts["package"]):
        raise InvalidIdentifier(
            "Package name {} is not a valid " "identifier.".format(opts["package"])
        )

    if opts["update"] and not opts["force"]:
        if not info.is_git_workspace_clean(opts["project_path"]):
            raise GitDirtyWorkspace

    return struct, opts


def verify_project_dir(struct, opts):
    """Check if PyScaffold can materialize the project dir structure.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        dict, dict: updated project representation and options
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


def init_git(struct, opts):
    """Add revision control to the generated files.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        dict, dict: updated project representation and options
    """
    if not opts["update"] and not repo.is_git_repo(opts["project_path"]):
        repo.init_commit_repo(
            opts["project_path"], struct, log=True, pretend=opts.get("pretend")
        )

    return struct, opts


# -------- API --------

DEFAULT_ACTIONS = [
    get_default_options,
    verify_options_consistency,
    define_structure,
    verify_project_dir,
    version_migration,
    create_structure,
    init_git,
]


def create_project(opts=None, **kwargs):
    """Create the project's directory structure

    Args:
        opts (dict): options of the project
        **kwargs: extra options, passed as keyword arguments

    Returns:
        tuple: a tuple of `struct` and `opts` dictionary

    Valid options include:

    :Project Information:   - **project_path** (:class:`os.PathLike`)

    :Naming:                - **name** (*str*)
                            - **package** (*str*)

    :Package Information:   - **author** (*str*)
                            - **email** (*str*)
                            - **release_date** (*str*)
                            - **year** (*str*)
                            - **title** (*str*)
                            - **description** (*str*)
                            - **url** (*str*)
                            - **classifiers** (*str*)
                            - **requirements** (*list*)

    :PyScaffold Control:    - **update** (*bool*)
                            - **force** (*bool*)
                            - **pretend** (*bool*)
                            - **extensions** (*list*)

    Some of these options are equivalent to the command line options, others
    are used for creating the basic python package meta information, but the
    last tree can change the way PyScaffold behaves.

    When the **force** flag is ``True``, existing files will be overwritten.
    When the **update** flag is ``True``, PyScaffold will consider that some
    files can be updated (usually the packaging boilerplate),
    but will keep others intact.
    When the **pretend** flag is ``True``, the project will not be
    created/updated, but the expected outcome will be logged.

    Finally, the **extensions** list may contain any function that follows the
    `extension API <../extensions>`_. Note that some PyScaffold features, such
    as travis, tox and pre-commit support, are implemented as built-in
    extensions.  In order to use these features it is necessary to include the
    respective functions in the extension list.  All built-in extensions are
    accessible via :mod:`pyscaffold.extensions` submodule.

    Note that extensions may define extra options. For example, the
    cookiecutter extension define a ``cookiecutter`` option that
    should be the address to the git repository used as template.
    """
    opts = bootstrap_options(opts, **kwargs)
    actions = discover_actions(opts["extensions"])

    # call the actions to generate final struct and opts
    struct = {}
    struct, opts = reduce(
        lambda acc, f: invoke_action(f, *acc), actions, (struct, opts)
    )
    return struct, opts


# -------- Auxiliary functions --------


def _activate(extension, actions):
    """Activate extension with proper logging."""
    logger.report("activate", extension.__module__)
    with logger.indent():
        actions = extension(actions)

    return actions


def _read_existing_config(opts):
    """Read existing config files first listed in ``opts["config_files"]``
    and then ``setup.cfg`` inside ``opts["project_path"]``
    """
    config_files = opts["config_files"]
    if config_files is not NO_CONFIG:
        paths = (Path(f).resolve() for f in config_files)
        deduplicated = {p: p for p in paths}
        # ^  using a dict instead of a set to preserve the order the files were given
        # ^  we do not mute errors here if the file does not exist. Let us be
        #    explicit.
        opts = reduce(lambda acc, f: info.project(acc, f), deduplicated.keys(), opts)

    if opts["update"]:
        try:
            opts = info.project(opts)
            # ^  In case of an update read and parse setup.cfg inside project
        except Exception as e:
            raise NoPyScaffoldProject from e

    return opts
