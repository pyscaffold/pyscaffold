# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import imp
import copy
import socket
import getpass
import random

import sh

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
    try:
        imp.load_source("versioneer",
                        os.path.join(args.project, "versioneer.py"))
    except:
        raise RuntimeError("Could not load versioneer.py!")
    try:
        # Generate setup with random module name since this function might be
        # called several times (in unittests) and imp.load_source seems to
        # not properly reload an already loaded file.
        mod_name = "setup_{rand}".format(rand=random.getrandbits(16))
        setup = imp.load_source(mod_name,
                                os.path.join(args.project, "setup.py"))
    except:
        raise RuntimeError("Could not load setup.py!")
    try:
        if not args.description:
            args.description = setup.DESCRIPTION
        if not args.license:
            args.license = setup.LICENSE
        if not args.url:
            args.url = setup.URL
        args.package = setup.MAIN_PACKAGE
    except:
        raise RuntimeError("Could not update {project}. Was it generated with "
                           "PyScaffold?".format(project=args.project))
    return args
