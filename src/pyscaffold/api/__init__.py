# -*- coding: utf-8 -*-
"""
Exposed API for accessing PyScaffold via Python.
"""

import os
from datetime import date, datetime
from functools import reduce

import pyscaffold

from .. import info, repo, utils
from ..exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitDirtyWorkspace,
    InvalidIdentifier
)
from ..log import logger
from ..structure import (
    create_structure,
    define_structure
)
from ..update import (
    apply_update_rules,
    version_migration,
    invoke_action
)
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
        return '--{flag}'.format(flag=utils.dasherize(self.name))

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
            self.flag,
            help=help,
            dest="extensions",
            action="append_const",
            const=self)
        return self

    def activate(self, actions):
        """Activates the extension by registering its functionality

        Args:
            actions (list): list of action to perform

        Returns:
            list: updated list of actions
        """
        raise NotImplementedError(
            "Extension {} has no actions registered".format(self.name))

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


# -------- Actions --------

DEFAULT_OPTIONS = {'update': False,
                   'force': False,
                   'description': 'Add a short description here!',
                   'url': 'https://github.com/pyscaffold/pyscaffold/',
                   'license': 'mit',
                   'version': pyscaffold.__version__,
                   'classifiers': ['Development Status :: 4 - Beta',
                                   'Programming Language :: Python'],
                   }


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

    # Order the extensions lexicographically which is needed for determinism,
    # also internal before external "pyscaffold.*" < "pyscaffoldext.*"
    def sort_by_qual_name(ext):
        return '.'.join([ext.__module__, ext.__class__.__qualname__])

    extensions = sorted(extensions, key=sort_by_qual_name)
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

    given_opts = opts
    # Initial parameters that need to be provided also during an update
    opts = DEFAULT_OPTIONS.copy()
    opts.update(given_opts)
    opts.setdefault('package', utils.make_valid_identifier(opts['project']))
    opts.setdefault('author', info.username())
    opts.setdefault('email', info.email())
    opts.setdefault('release_date', date.today().strftime('%Y-%m-%d'))
    # All kinds of derived parameters
    year = datetime.strptime(opts['release_date'], '%Y-%m-%d').year
    opts.setdefault('year', year)
    opts.setdefault('title',
                    '='*len(opts['project']) + '\n' + opts['project'] + '\n' +
                    '='*len(opts['project']))

    # Initialize empty list of all requirements and extensions
    # (since not using deep_copy for the DEFAULT_OPTIONS, better add compound
    # values inside this function)
    opts.setdefault('requirements', list())
    opts.setdefault('extensions', list())
    opts.setdefault('root_pkg', opts['package'])
    opts.setdefault('qual_pkg', opts['package'])
    opts.setdefault('cli_params', {'extensions': list(), 'args': dict()})
    opts.setdefault('pretend', False)

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
    if not utils.is_valid_identifier(opts['package']):
        raise InvalidIdentifier(
            "Package name {} is not a valid "
            "identifier.".format(opts['package']))

    if opts['update'] and not opts['force']:
        if not info.is_git_workspace_clean(opts['project']):
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
    if os.path.exists(opts['project']):
        if not opts['update'] and not opts['force']:
            raise DirectoryAlreadyExists(
                "Directory {dir} already exists! Use the `update` option to "
                "update an existing project or the `force` option to "
                "overwrite an existing directory.".format(dir=opts['project']))
    elif opts['update']:
        raise DirectoryDoesNotExist(
            "Project {project} does not exist and thus cannot be "
            "updated!".format(project=opts['project']))

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
    if not opts['update'] and not repo.is_git_repo(opts['project']):
        repo.init_commit_repo(opts['project'], struct,
                              log=True, pretend=opts.get('pretend'))

    return struct, opts


# -------- API --------

DEFAULT_ACTIONS = [
    get_default_options,
    verify_options_consistency,
    define_structure,
    verify_project_dir,
    apply_update_rules,
    version_migration,
    create_structure,
    init_git
]


def create_project(opts=None, **kwargs):
    """Create the project's directory structure

    Args:
        opts (dict): options of the project
        **kwargs: extra options, passed as keyword arguments

    Returns:
        tuple: a tuple of `struct` and `opts` dictionary

    Valid options include:

    :Naming:                - **project** (*str*)
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

    Note that extensions may define extra options. For example, built-in
    cookiecutter extension define a ``cookiecutter`` option that
    should be the address to the git repository used as template.
    """
    opts = opts if opts else {}
    opts.update(kwargs)

    actions = discover_actions(opts.get('extensions', []))

    # call the actions to generate final struct and opts
    struct = {}
    struct, opts = reduce(lambda acc, f: invoke_action(f, *acc),
                          actions, (struct, opts))
    return struct, opts


# -------- Auxiliary functions --------

def _activate(extension, actions):
    """Activate extension with proper logging."""
    logger.report('activate', extension.__module__)
    with logger.indent():
        actions = extension(actions)

    return actions
