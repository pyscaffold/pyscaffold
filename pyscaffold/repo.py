# -*- coding: utf-8 -*-
"""
Functionality for working with a git repository
"""
from __future__ import absolute_import, print_function

from os.path import join as join_path
from subprocess import CalledProcessError

from six import string_types

from . import utils
from . import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def git_tree_add(struct, prefix=""):
    """Adds recursively a directory structure to git

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        prefix (str): prefix for the given directory structure
    """
    for name, content in struct.items():
        if isinstance(content, string_types):
            shell.git('add', join_path(prefix, name))
        elif isinstance(content, dict):
            git_tree_add(struct[name], prefix=join_path(prefix, name))
        elif content is None:
            shell.git('add', join_path(prefix, name))
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))


def add_tag(project, tag_name, message=None):
    """Add an (annotated) tag to the git repository.

    Args:
        project (str): path to the project
        tag_name (str): name of the tag
        message (str): optional tag message
    """
    with utils.chdir(project):
        if message is None:
            shell.git('tag', tag_name)
        else:
            shell.git('tag', '-a', tag_name, '-m', message)


def init_commit_repo(project, struct):
    """Initialize a git repository

    Args:
        project (str): path to the project
        struct (dict): directory structure as dictionary of dictionaries
    """
    with utils.chdir(project):
        shell.git('init')
        git_tree_add(struct[project])
        shell.git('commit', '-m', 'Initial commit')


def is_git_repo(folder):
    """Check if a folder is a git repository

    Args:
        folder (str): path
    """
    with utils.chdir(folder):
        try:
            shell.git('rev-parse', '--git-dir')
        except CalledProcessError:
            return False
        return True


def get_git_root(default=None):
    """Return the path to the top-level of the git repository or *default*.

    Args:
        default (str): if no git root is found, default is returned

    Returns:
        str: top-level path or *default*
    """
    if shell.git is None:
        return default
    try:
        return next(shell.git('rev-parse', '--show-toplevel'))
    except CalledProcessError:
        return default
