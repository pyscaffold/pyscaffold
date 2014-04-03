# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import socket
import getpass

import git


def get_global_gitconfig():
    home = os.path.expanduser("~")
    gitconfig_file = os.path.join(home, ".gitconfig")
    return git.config.GitConfigParser(gitconfig_file)


def username():
    git_cfg = get_global_gitconfig()
    try:
        user = git_cfg.get("user", "name")
    except:
        user = getpass.getuser()
    return user


def email():
    git_cfg = get_global_gitconfig()
    try:
        email = git_cfg.get("user", "email")
    except:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return email