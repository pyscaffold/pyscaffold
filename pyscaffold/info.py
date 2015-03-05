# -*- coding: utf-8 -*-
"""
Provide general information about the system, user etc.
"""
from __future__ import absolute_import, print_function

import copy
import getpass
import imp
import os
import random
import socket
from subprocess import CalledProcessError

from six.moves import configparser

from . import shell, utils
from .templates import best_fit_license

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def username():
    """
    Retrieve the user's name

    :return: user's name as string
    """
    try:
        user = next(shell.git("config", "--global", "--get", "user.name"))
        user = user.strip()
    except CalledProcessError:
        user = getpass.getuser()
    return utils.utf8_decode(user)


def email():
    """
    Retrieve the user's email

    :return: user's email as string
    """
    try:
        email = next(shell.git("config", "--global", "--get", "user.email"))
        email = email.strip()
    except CalledProcessError:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return utils.utf8_decode(email)


def is_git_installed():
    """
    Check if git is installed

    :return: boolean
    """
    try:
        shell.git("--version")
    except CalledProcessError:
        return False
    return True


def is_git_configured():
    """
    Check if user.name and user.email is set globally in git

    :return: boolean
    """
    try:
        for attr in ["name", "email"]:
            shell.git("config", "--global", "--get", "user.{}".format(attr))
    except CalledProcessError:
        return False
    return True


def read_setup_py(args):
    """
    Read setup.py (PyScaffold < 2.0) for user settings

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: updated command line parameters as :obj:`argparse.Namespace`
    """
    imp.load_source("versioneer", os.path.join(args.project, "versioneer.py"))
    # Generate setup with random module name since this function might be
    # called several times (in unittests) and imp.load_source seems to
    # not properly reload an already loaded file.
    mod_name = "setup_{rand}".format(rand=random.getrandbits(32))
    setup = imp.load_source(mod_name, os.path.join(args.project, "setup.py"))
    if args.description is None:
        args.description = setup.DESCRIPTION
    if args.license is None:
        args.license = best_fit_license(setup.LICENSE)
    if args.url is None:
        args.url = setup.URL
    args.package = setup.MAIN_PACKAGE
    args.console_scripts = "\n".join(setup.CONSOLE_SCRIPTS)
    if args.console_scripts:  # append newline for aesthetic reasons
        args.console_scripts += "\n"
    args.classifiers = utils.list2str(setup.CLASSIFIERS, indent=15)
    return args


def read_setup_cfg(args):
    """
    Read setup.cfg (PyScaffold >= 2.0) for user settings

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: updated command line parameters as :obj:`argparse.Namespace`
    """
    config = configparser.SafeConfigParser()
    config.read(os.path.join(args.project, 'setup.cfg'))
    if args.description is None:
        args.description = config.get('metadata', 'description')
    if args.license is None:
        args.license = best_fit_license(config.get('metadata', 'license'))
    if args.url is None:
        args.url = config.get('metadata', 'url')
    args.classifiers = config.get('metadata', 'classifiers')
    args.console_scripts = "\n".join(["{} = {}".format(k, v) for k, v
                                      in config.items('console_scripts')])
    if args.console_scripts:  # append newline for aesthetic reasons
        args.console_scripts += "\n"
    return args


def project(args):
    """
    Update user settings with the settings of an existing PyScaffold project

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: updated command line parameters as :obj:`argparse.Namespace`
    """
    args = copy.copy(args)
    if not os.path.exists(args.project):
        raise RuntimeError("Project {project} does not"
                           " exist!".format(project=args.project))
    for read_config in [read_setup_py, read_setup_cfg]:
        try:
            args = read_config(args)
        except (IOError, AttributeError, configparser.Error):
            continue
        else:
            break
    else:
        raise RuntimeError("Could not update {project}. Was it generated "
                           "with PyScaffold?".format(project=args.project))
    return args
