# -*- coding: utf-8 -*-
"""
Exposed API for accessing PyScaffold via Python.
"""
from __future__ import absolute_import

import os
from datetime import date
from functools import reduce

import pyscaffold

from .. import info, repo, utils
from ..exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
    InvalidIdentifier
)
from ..log import logger
from ..structure import (
    apply_update_rules,
    create_structure,
    define_structure
)
from . import helpers

# -------- Actions --------

DEFAULT_OPTIONS = {'update': False,
                   'force': False,
                   'description': 'Add a short description here!',
                   'url': 'http://...',
                   'license': 'none',
                   'version': pyscaffold.__version__,
                   'classifiers': utils.list2str(
                        ['Development Status :: 4 - Beta',
                         'Programming Language :: Python'],
                        indent=4, brackets=False, quotes=False, sep='')}


def get_default_options(struct, given_opts):
    """Compute all the options that can be automatically derived.

    This function uses all the available information to generate sensible
    defaults. Several options that can be derived are computed when possible.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        given_opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        dict: options with default values set

    Raises:
        :class:`~.DirectoryDoesNotExist`: when PyScaffold is told to
            update an inexistent directory
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information

    Note:
        This function uses git to determine some options, such as author name
        and email.
    """

    # This function uses information from git, so make sure it is available
    _verify_git()

    opts = DEFAULT_OPTIONS.copy()
    opts.update(given_opts)
    project_name = opts['project']

    opts.setdefault('package', utils.make_valid_identifier(opts['project']))
    opts.setdefault('author', info.username())
    opts.setdefault('email', info.email())
    opts.setdefault('release_date', date.today().strftime('%Y-%m-%d'))
    opts.setdefault('year', date.today().year)
    opts.setdefault('title',
                    '='*len(opts['project']) + '\n' + opts['project'] + '\n' +
                    '='*len(opts['project']))

    # Initialize empty list of all requirements and extensions
    # (since not using deep_copy for the DEFAULT_OPTIONS, better add compound
    # values inside this function)
    opts.setdefault('requirements', list())
    opts.setdefault('extensions', list())

    opts.setdefault('root_pkg', opts['package'])
    opts.setdefault('namespace_pkg', opts['package'])

    if opts['update']:
        if not os.path.exists(project_name):
            raise DirectoryDoesNotExist(
                "Project {project} does not exist and thus cannot be "
                "updated!".format(project=project_name))
        opts = info.project(opts)
        # Reset project name since the one from setup.cfg might be different
        opts['project'] = project_name

    opts.setdefault('pretend', False)

    return (struct, opts)


def verify_options_consistency(struct, opts):
    """Perform some sanity checks about the given options."""
    if os.path.exists(opts['project']):
        if not opts['update'] and not opts['force']:
            raise DirectoryAlreadyExists(
                "Directory {dir} already exists! Use the `update` option to "
                "update an existing project or the `force` option to "
                "overwrite an existing directory.".format(dir=opts['project']))
    if not utils.is_valid_identifier(opts['package']):
        raise InvalidIdentifier(
            "Package name {} is not a valid "
            "identifier.".format(opts['package']))

    return (struct, opts)


def init_git(struct, opts):
    """Add revision control to the generated files."""
    if not opts['update'] and not repo.is_git_repo(opts['project']):
        repo.init_commit_repo(opts['project'], struct,
                              log=True, pretend=opts.get('pretend'))

    return (struct, opts)


# -------- API --------

DEFAULT_ACTIONS = [
    get_default_options,
    verify_options_consistency,
    define_structure,
    apply_update_rules,
    create_structure,
    init_git
]


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
    actions = DEFAULT_ACTIONS

    # Activate the extensions
    return reduce(lambda acc, f: _activate(f, acc), extensions, actions)


def create_project(opts=None, **kwargs):
    """Create the project's directory structure

    Args:
        opts (dict): options of the project
        **kwargs: extra options, passed as keyword arguments

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
    accessible via :mod:`pyscaffold.extensions` submodule, and use
    ``extend_project`` as naming convention::

        # Using built-in extensions
        from pyscaffold.extensions import pre_commit, travis, tox

        opts = { #...
                 "extensions": [e.extend_project
                                for e in pre_commit, travis, tox]}
        create_project(opts)

    Note that extensions may define extra options. For example, built-in
    cookiecutter extension define a ``cookiecutter_template`` option that
    should be the address to the git repository used as template.
    """
    opts = opts if opts else {}
    opts.update(kwargs)

    actions = discover_actions(opts.get('extensions',  []))

    # Call the actions
    return reduce(lambda acc, f: _invoke(f, *acc), actions, ({}, opts))


# -------- Auxiliary functions --------

def _activate(extension, actions):
    """Activate extension with proper logging."""
    logger.report('activate', extension.__module__)
    with logger.indent():
        actions = extension(actions, helpers)

    return actions


def _invoke(action, struct, opts):
    """Invoke action with proper logging."""
    logger.report('invoke', helpers.get_id(action))
    with logger.indent():
        struct, opts = action(struct, opts)

    return (struct, opts)


def _verify_git():
    """Check if git is installed and able to provide the required information.
    """
    if not info.is_git_installed():
        raise GitNotInstalled
    if not info.is_git_configured():
        raise GitNotConfigured
