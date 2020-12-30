"""
Functionality for working with a git repository
"""

from pathlib import Path
from typing import Optional, TypeVar, Union

from . import shell
from .exceptions import ShellCommandException
from .file_system import PathLike, chdir

T = TypeVar("T")


def git_tree_add(struct: dict, prefix: PathLike = "", **kwargs):
    """Adds recursively a directory structure to git

    Args:
        struct: directory structure as dictionary of dictionaries
        prefix: prefix for the given directory structure

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    prefix = Path(prefix)
    for name, content in struct.items():
        if isinstance(content, dict):
            git_tree_add(struct[name], prefix=prefix / name, **kwargs)
        elif content is None or isinstance(content, str):
            shell.git("add", str(prefix / name), **kwargs)
        else:
            raise TypeError(f"Don't know what to do with content type {type}.")


def add_tag(project: PathLike, tag_name: str, message: Optional[str] = None, **kwargs):
    """Add an (annotated) tag to the git repository.

    Args:
        project: path to the project
        tag_name: name of the tag
        message: optional tag message

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    with chdir(project):
        if message is None:
            shell.git("tag", tag_name, **kwargs)
        else:
            shell.git("tag", "-a", tag_name, "-m", message, **kwargs)


def init_commit_repo(project: PathLike, struct: dict, **kwargs):
    """Initialize a git repository

    Args:
        project: path to the project
        struct: directory structure as dictionary of dictionaries

    Additional keyword arguments are passed to the
    :obj:`git <pyscaffold.shell.ShellCommand>` callable object.
    """
    with chdir(project, pretend=kwargs.get("pretend")):
        shell.git("init", **kwargs)
        git_tree_add(struct, **kwargs)
        shell.git("commit", "-m", "Initial commit", **kwargs)


def is_git_repo(folder: PathLike):
    """Check if a folder is a git repository"""
    folder = Path(folder)
    if not folder.is_dir():
        return False

    with chdir(folder):
        try:
            shell.git("rev-parse", "--git-dir")
        except ShellCommandException:
            return False
        return True


def get_git_root(default: Optional[T] = None) -> Union[None, T, str]:
    """Return the path to the top-level of the git repository or *default*.

    Args:
        default: if no git root is found, default is returned

    Returns:
        str: top-level path or *default*
    """
    if shell.git is None:
        return default
    try:
        return next(shell.git("rev-parse", "--show-toplevel"))
    except ShellCommandException:
        return default
