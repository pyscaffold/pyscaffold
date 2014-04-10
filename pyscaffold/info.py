# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import re
import socket
import getpass
import keyword

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


def is_valid_identifier(string):
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
    string = string.strip()
    string = string.replace("-", "_")
    string = string.replace(" ", "_")
    string = re.sub('[^_a-zA-Z0-9]', '', string)
    if is_valid_identifier(string):
        return string
    else:
        raise RuntimeError("String cannot be converted to a valid identifier.")
