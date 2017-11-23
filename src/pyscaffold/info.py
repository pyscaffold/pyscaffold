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
from . import shell, utils
from .exceptions import ShellCommandException


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

    Returns:
        bool: True if it is set globally, False otherwise
    """
    try:
        for attr in ["name", "email"]:
            shell.git("config", "--get", "user.{}".format(attr))
    except ShellCommandException:
        return False
    return True


def project(opts):
    """Update user options with the options of an existing PyScaffold project

    Params:
        opts (dict): options of the project

    Returns:
        dict: options with updated values
    """
    from setuptools import find_packages

    opts = copy.copy(opts)
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(opts['project'], 'setup.cfg'))
        opts['project'] = config.get('metadata', 'name')
        opts['description'] = config.get('metadata', 'description')
        opts['author'] = config.get('metadata', 'author')
        opts['email'] = config.get('metadata', 'author-email')
        opts['license'] = utils.best_fit_license(
            config.get('metadata', 'license'))
        opts['url'] = config.get('metadata', 'home-page')
        opts['classifiers'] = config.get('metadata', 'classifiers')
        opts['package'] = find_packages(
            os.path.join(opts['project'], 'src'))[0]
    except Exception as e:
        print(e)
        raise RuntimeError("Could not update {project}. Was it generated "
                           "with PyScaffold?".format(project=opts['project']))
    return opts
