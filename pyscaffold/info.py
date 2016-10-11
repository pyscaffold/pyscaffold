# -*- coding: utf-8 -*-
"""
Provide general information about the system, user etc.
"""
from __future__ import absolute_import, print_function

import copy
import getpass
import os
import socket
from subprocess import CalledProcessError

from six.moves import configparser

from . import shell, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def username():
    """Retrieve the user's name

    Returns:
        str: user's name
    """
    try:
        user = next(shell.git("config", "--get", "user.name"))
        user = user.strip()
    except CalledProcessError:
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
    except CalledProcessError:
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
    except CalledProcessError:
        return False
    return True


def is_git_configured():
    """Check if user.name and user.email is set globally in git

    Returns:
        bool: True if it is set globally, False otherwise
    """
    try:
        for attr in ["name", "email"]:
            shell.git("config", "--get", "user.{}".format(attr))
    except CalledProcessError:
        return False
    return True


def project(opts):
    """Update user options with the options of an existing PyScaffold project

    Params:
        opts (dict): options of the project

    Returns:
        dict: options with updated values
    """
    opts = copy.copy(opts)
    try:
        config = configparser.SafeConfigParser()
        config.read(os.path.join(opts['project'], 'setup.cfg'))
        # Some branches due to backward compatibility
        if config.has_option('metadata', 'name'):
            opts['project'] = config.get('metadata', 'name')
        if config.has_option('metadata', 'description'):
            opts['description'] = config.get('metadata', 'description')
        else:
            opts['description'] = config.get('metadata', 'summary')
        opts['author'] = config.get('metadata', 'author')
        if config.has_option('metadata', 'author_email'):
            opts['email'] = config.get('metadata', 'author_email')
        else:
            opts['email'] = config.get('metadata', 'author-email')
        opts['license'] = utils.best_fit_license(
            config.get('metadata', 'license'))
        if config.has_option('metadata', 'url'):
            opts['url'] = config.get('metadata', 'url')
        else:
            opts['url'] = config.get('metadata', 'home-page')
        if config.has_option('metadata', 'classifiers'):
            opts['classifiers'] = config.get('metadata', 'classifiers')
        if config.has_option('files', 'packages'):
            opts['package'] = config.get('files', 'packages').strip()
    except Exception as e:
        print(e)
        raise RuntimeError("Could not update {project}. Was it generated "
                           "with PyScaffold?".format(project=opts['project']))
    return opts
