# -*- coding: utf-8 -*-
"""
Functionality for working with a git repository
"""
from __future__ import absolute_import, print_function

from os.path import join as join_path
from subprocess import CalledProcessError

from six import string_types

from . import utils
from .shell import git

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def git_tree_add(struct, prefix=""):
    """
    Adds recursively a directory structure to git

    :param struct: directory structure as dictionary of dictionaries
    :param prefix: prefix for the given directory structure as string
    """
    for name, content in struct.items():
        if isinstance(content, string_types):
            git("add", join_path(prefix, name))
        elif isinstance(content, dict):
            git_tree_add(struct[name], prefix=join_path(prefix, name))
        elif content is None:
            git("add", join_path(prefix, name))
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))


def add_tag(project, tag_name, message=None):
    """
    Add an (annotated) tag to the git repository.

    :param project: path to the project as string
    :param tag_name: name of the tag as string
    :param message: optional tag message as string
    """
    with utils.chdir(project):
        if message is None:
            git("tag", tag_name)
        else:
            git("tag", "-a", tag_name, "-m", message)


def init_commit_repo(project, struct):
    """
    Initialize a git repository

    :param project: path to the project as string
    :param struct: directory structure as dictionary of dictionaries
    """
    with utils.chdir(project):
        git("init")
        git_tree_add(struct[project])
        git("commit", "-m", "Initial commit")


def is_git_repo(folder):
    """
    Check if a folder is a git repository

    :param folder: path as string
    """
    with utils.chdir(folder):
        try:
            git("rev-parse", "--git-dir")
        except CalledProcessError:
            return False
        return True
