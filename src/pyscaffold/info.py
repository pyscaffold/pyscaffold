# -*- coding: utf-8 -*-
"""
Provide general information about the system, user etc.
"""
from __future__ import absolute_import, print_function

import copy
import getpass
import os
import socket

from .contrib.six.moves import configparser
from .contrib.six import raise_from
from . import shell, utils
from .exceptions import (
    ShellCommandException,
    GitNotInstalled,
    GitNotConfigured,
    PyScaffoldTooOld,
    NoPyScaffoldProject)


def username():
    """Retrieve the user's name

    Returns:
        str: user's name
    """
    try:
        user = next(shell.git("config", "--get", "user.name"))
        user = user.strip()
    except ShellCommandException:
        user = getpass.getuser()
    return utils.utf8_decode(user)


def email():
    """Retrieve the user's email

    Returns:
        str: user's email
    """
    try:
        email = next(shell.git("config", "--get", "user.email"))
        email = email.strip()
    except ShellCommandException:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return utils.utf8_decode(email)


def is_git_installed():
    """Check if git is installed

    Returns:
        bool: True if git is installed, False otherwise
    """
    if shell.git is None:
        return False
    try:
        shell.git("--version")
    except ShellCommandException:
        return False
    return True


def is_git_configured():
    """Check if user.name and user.email is set globally in git

    This will also return false if git is not available at all.

    Returns:
        bool: True if it is set globally, False otherwise
    """
    try:
        for attr in ["name", "email"]:
            shell.git("config", "--get", "user.{}".format(attr))
    except ShellCommandException:
        return False
    return True


def check_git():
    """Checks for git and raises appropriate exception if not

     Raises:
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information
    """
    if not is_git_installed():
        raise GitNotInstalled
    if not is_git_configured():
        raise GitNotConfigured


def project(opts):
    """Update user options with the options of an existing PyScaffold project

    Params:
        opts (dict): options of the project

    Returns:
        dict: options with updated values

    Raises:
        :class:`~.PyScaffoldTooOld`: when PyScaffold is to old to update from
        :class:`~.NoPyScaffoldProject`: when project was not generated with
            PyScaffold
    """
    from pkg_resources import iter_entry_points

    opts = copy.deepcopy(opts)
    try:
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(opts['project'], 'setup.cfg'))
        if not cfg.has_section('pyscaffold'):
            raise PyScaffoldTooOld
        pyscaffold = cfg['pyscaffold']
        metadata = cfg['metadata']
        # This would be needed in case of inplace updates, see issue #138
        # if opts['project'] == '.':
        #     opts['project'] = metadata['name']
        # Overwrite only if user has not provided corresponding cli argument
        opts.setdefault('package', pyscaffold['package'])
        opts.setdefault('author', metadata['author'])
        opts.setdefault('email', metadata['author-email'])
        opts.setdefault('url', metadata['url'])
        opts.setdefault('description', metadata['description'])
        opts.setdefault('license', utils.best_fit_license(metadata['license']))
        # Additional parameters compare with `get_default_options`
        opts['classifiers'] = metadata['classifiers'].strip().split('\n')
        opts['version'] = pyscaffold['version']
        # complement the cli extensions with the ones from configuration
        if 'extensions' in pyscaffold:
            cfg_extensions = pyscaffold['extensions'].strip().split('\n')
            opt_extensions = [ext.name for ext in opts['extensions']]
            add_extensions = set(cfg_extensions) - set(opt_extensions)
            for extension in iter_entry_points('pyscaffold.cli'):
                if extension.name in add_extensions:
                    extension_obj = extension.load()(extension.name)
                    if extension.name in pyscaffold:
                        ext_value = pyscaffold[extension.name]
                        extension_obj.args = ext_value
                        opts[extension.name] = ext_value
                    opts['extensions'].append(extension_obj)
    except Exception as e:
        raise raise_from(NoPyScaffoldProject, e)
    return opts
