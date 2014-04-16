# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import imp
import copy
import socket
import getpass

import sh

from . import utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def username():
    try:
        user = sh.git("config", "--global", "--get", "user.name").next()
        user = str(user).strip()
    except:
        user = getpass.getuser()
    return user


def email():
    try:
        email = sh.git("config", "--global", "--get", "user.email").next()
        email = str(email).strip()
    except:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return email


def git_is_installed():
    try:
        sh.git("--version")
    except:
        return False
    return True


def project(args):
    args = copy.copy(args)
    if not os.path.exists(args.project):
        raise RuntimeError("Project {project} does not"
                           " exist!".format(project=args.project))
    setup = imp.load_source("setup", os.path.join(args.project, "setup.py"))
    if not args.description:
        args.description = setup.DESCRIPTION
    if not args.license:
        args.license = setup.LICENSE
    if not args.url:
        args.url = setup.URL
    args.package = setup.MAIN_PACKAGE
    return args
