# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import socket
import getpass

from sh import git

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def username():
    try:
        user = git("config", "--global", "--get", "user.name").next()
        user = str(user).strip()
    except:
        user = getpass.getuser()
    return user


def email():
    try:
        email = git("config", "--global", "--get", "user.email").next()
        email = str(email).strip()
    except:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return email


def git_is_installed():
    try:
        git("--version")
    except:
        return False
    return True