# -*- coding: utf-8 -*-
"""
Provide general information about the system, user etc.
"""

import copy
import getpass
import os
import socket
from enum import Enum
from operator import itemgetter

from . import shell
from .exceptions import (
    GitNotConfigured,
    GitNotInstalled,
    PyScaffoldTooOld,
    ShellCommandException,
)
from .log import logger
from .templates import licenses
from .update import read_setupcfg
from .utils import chdir, levenshtein, setdefault


class GitEnv(Enum):
    author_name = "GIT_AUTHOR_NAME"
    author_email = "GIT_AUTHOR_EMAIL"
    author_date = "GIT_AUTHOR_DATE"
    committer_name = "GIT_COMMITTER_NAME"
    committer_email = "GIT_COMMITTER_EMAIL"
    committer_date = "GIT_COMMITTER_DATE"


def username():
    """Retrieve the user's name

    Returns:
        str: user's name
    """
    user = os.getenv(GitEnv.author_name.value)
    if user is None:
        try:
            user = next(shell.git("config", "--get", "user.name"))
            user = user.strip()
        except ShellCommandException:
            try:
                # On Windows the getpass commands might fail if 'USERNAME'
                # env var is not set
                user = getpass.getuser()
            except Exception as ex:
                logger.debug("Impossible to find hostname", exc_info=True)
                raise GitNotConfigured from ex
    return user


def email():
    """Retrieve the user's email

    Returns:
        str: user's email
    """
    mail = os.getenv(GitEnv.author_email.value)
    if mail is None:
        try:
            mail = next(shell.git("config", "--get", "user.email"))
            mail = mail.strip()
        except ShellCommandException:
            try:
                # On Windows the getpass commands might fail
                user = getpass.getuser()
                host = socket.gethostname()
                mail = "{user}@{host}".format(user=user, host=host)
            except Exception as ex:
                logger.debug("Impossible to find user/hostname", exc_info=True)
                raise GitNotConfigured from ex
    return mail


def is_git_installed():
    """Check if git is installed

    Returns:
        bool: True if git is installed, False otherwise
    """
    if shell.git is None:
        return False
    try:
        shell.git("--version")
    except ShellCommandException:
        return False
    return True


def is_git_configured():
    """Check if user.name and user.email is set globally in git

    Check first git environment variables, then config settings.
    This will also return false if git is not available at all.

    Returns:
        bool: True if it is set globally, False otherwise
    """
    if os.getenv(GitEnv.author_name.value) and os.getenv(GitEnv.author_email.value):
        return True
    else:
        try:
            for attr in ("name", "email"):
                shell.git("config", "--get", "user.{}".format(attr))
        except ShellCommandException:
            return False
        else:
            return True


def check_git():
    """Checks for git and raises appropriate exception if not

     Raises:
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information
    """
    if not is_git_installed():
        raise GitNotInstalled
    if not is_git_configured():
        raise GitNotConfigured


def is_git_workspace_clean(path):
    """Checks if git workspace is clean

    Args:
        path (str): path to git repository

    Returns:
        bool: condition if workspace is clean or not

     Raises:
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information
    """
    # ToDo: Change to pathlib for v4
    check_git()
    try:
        with chdir(path):
            shell.git("diff-index", "--quiet", "HEAD", "--")
    except ShellCommandException:
        return False
    return True


def project(opts, config_path=None, config_file=None):
    """Update user options with the options of an existing config file

    Params:
        opts (dict): options of the project
        config_path (os.PathLike): path where config file can be
            found (default: ``opts["project_path"]``)
        config_file (os.PathLike): if ``config_path`` is a directory,
            name of the config file, relative to it (default: ``setup.cfg``)

    Returns:
        dict: options with updated values

    Raises:
        :class:`~.PyScaffoldTooOld`: when PyScaffold is to old to update from
        :class:`~.NoPyScaffoldProject`: when project was not generated with
            PyScaffold
    """
    from pkg_resources import iter_entry_points

    opts = copy.deepcopy(opts)
    config_path = config_path or opts.get("project_path")

    cfg = read_setupcfg(config_path, config_file).to_dict()
    if "pyscaffold" not in cfg:
        raise PyScaffoldTooOld

    pyscaffold = cfg.pop("pyscaffold", {})
    metadata = cfg.pop("metadata", {})

    # Overwrite only if user has not provided corresponding cli argument
    setdefault(opts, "name", metadata.get("name"))
    setdefault(opts, "package", pyscaffold.pop("package", None))
    setdefault(opts, "author", metadata.get("author"))
    setdefault(opts, "email", metadata.get("author-email"))
    setdefault(opts, "url", metadata.get("url"))
    setdefault(opts, "description", metadata.get("description"))
    setdefault(opts, "license", best_fit_license(metadata.get("license", "")))
    # Additional parameters compare with `get_default_options`

    # Merge classifiers
    if "classifiers" in metadata:
        classifiers = (c.strip() for c in metadata["classifiers"].strip().split("\n"))
        classifiers = {c for c in classifiers if c}
        existing_classifiers = {c for c in opts.get("classifiers", []) if c}
        opts["classifiers"] = sorted(existing_classifiers | classifiers)

    # complement the cli extensions with the ones from configuration
    if "extensions" in pyscaffold:
        cfg_extensions = pyscaffold.pop("extensions").strip().split("\n")
        cfg_extensions = [e.strip() for e in cfg_extensions]
        opt_extensions = [ext.name for ext in opts["extensions"]]
        add_extensions = set(cfg_extensions) - set(opt_extensions)
        # TODO: sort extensions in the same way they are sorted in CLI for
        #       determism.
        for extension in iter_entry_points("pyscaffold.cli"):
            if extension.name in add_extensions:
                extension_obj = extension.load()(extension.name)
                # TODO: revisit the need of passing `args` to the extension_obj,
                #       do we really need it? Isn't it enough to have it stored
                #       in `opts`? If not necessary we can simply remove this if
                if extension.name in pyscaffold:
                    ext_value = pyscaffold.pop(extension.name)
                    extension_obj.args = ext_value
                    setdefault(opts, extension.name, ext_value)
                opts["extensions"].append(extension_obj)

    # The remaining values in the pyscaffold section can be added to opts
    # if not specified yet. Useful when extensions define other options.
    for key, value in pyscaffold.items():
        setdefault(opts, key, value)

    return opts


def best_fit_license(txt):
    """Finds proper license name for the license defined in txt

    Args:
        txt (str): license name

    Returns:
        str: license name
    """
    ratings = {lic: levenshtein(txt, lic.lower()) for lic in licenses}
    return min(ratings.items(), key=itemgetter(1))[0]
