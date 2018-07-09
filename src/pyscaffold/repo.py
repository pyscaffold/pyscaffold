# -*- coding: utf-8 -*-
"""
Functionality for working with a git repository
"""

from os.path import isdir
from os.path import join as join_path

from . import shell, utils
from .exceptions import ShellCommandException


def git_tree_add(struct, prefix="", **kwargs):
    """Adds recursively a directory structure to git

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        prefix (str): prefix for the given directory structure

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    for name, content in struct.items():
        if isinstance(content, str):
            shell.git('add', join_path(prefix, name), **kwargs)
        elif isinstance(content, dict):
            git_tree_add(
                struct[name], prefix=join_path(prefix, name), **kwargs)
        elif content is None:
            shell.git('add', join_path(prefix, name), **kwargs)
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))


def add_tag(project, tag_name, message=None, **kwargs):
    """Add an (annotated) tag to the git repository.

    Args:
        project (str): path to the project
        tag_name (str): name of the tag
        message (str): optional tag message

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    with utils.chdir(project):
        if message is None:
            shell.git('tag', tag_name, **kwargs)
        else:
            shell.git('tag', '-a', tag_name, '-m', message, **kwargs)


def init_commit_repo(project, struct, **kwargs):
    """Initialize a git repository

    Args:
        project (str): path to the project
        struct (dict): directory structure as dictionary of dictionaries

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    with utils.chdir(project, pretend=kwargs.get('pretend')):
        shell.git('init', **kwargs)
        git_tree_add(struct[project], **kwargs)
        shell.git('commit', '-m', 'Initial commit', **kwargs)


def is_git_repo(folder):
    """Check if a folder is a git repository

    Args:
        folder (str): path
    """
    if not isdir(folder):
        return False

    with utils.chdir(folder):
        try:
            shell.git('rev-parse', '--git-dir')
        except ShellCommandException:
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
    except ShellCommandException:
        return default
