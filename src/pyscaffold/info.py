"""
Provide general information about the system, user etc.
"""

import copy
import getpass
import os
import socket
from enum import Enum
from operator import itemgetter
from pathlib import Path

import appdirs

from . import __name__ as PKG_NAME
from . import shell
from .exceptions import (
    GitNotConfigured,
    GitNotInstalled,
    ImpossibleToFindConfigDir,
    PyScaffoldTooOld,
    ShellCommandException,
)
from .file_system import chdir
from .identification import deterministic_sort, levenshtein
from .log import logger
from .templates import licenses, parse_extensions
from .update import read_setupcfg

DEFAULT_CONFIG_FILE = "default.cfg"


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

    license = metadata.get("license")
    existing = {
        "package": pyscaffold.pop("package", None),
        "name": metadata.get("name"),
        "author": metadata.get("author"),
        "email": metadata.get("author-email"),
        "url": metadata.get("url"),
        "description": metadata.get("description"),
        "license": license and best_fit_license(license),
    }
    existing = {k: v for k, v in existing.items() if v}  # Filter out non stored values

    # Overwrite only if user has not provided corresponding cli argument
    # Derived/computed parameters should be set by `get_default_options`
    opts = {**existing, **opts}

    # Complement the cli extensions with the ones from configuration
    if "extensions" in pyscaffold:
        cfg_extensions = parse_extensions(pyscaffold.pop("extensions", ""))
        opt_extensions = {ext.name for ext in opts.setdefault("extensions", [])}
        add_extensions = cfg_extensions - opt_extensions

        opts["extensions"] += deterministic_sort(
            extension.load()(extension.name)
            for extension in iter_entry_points("pyscaffold.cli")
            if extension.name in add_extensions
        )

    # The remaining values in the pyscaffold section can be added to opts
    # if not specified yet. Useful when extensions define other options.
    for key, value in pyscaffold.items():
        opts.setdefault(key, value)

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


(RAISE_EXCEPTION,) = list(Enum("default", "RAISE_EXCEPTION"))  # type: ignore


def config_dir(prog=PKG_NAME, org=None, default=RAISE_EXCEPTION):
    """Finds the correct place where to read/write configurations for the given app.

    Args:
        prog (str): program name (defaults to pyscaffold)
        org (Optional[str]): organisation/author name (defaults to the same as ``prog``)
        default (Any): default value to return if an exception was raise while
            trying to find the config dir. If no default value is passed, an
            :obj:`~.ImpossibleToFindConfigDir` execution is raised.

    Please notice even if the directory doesn't exist, if its path is possible
    to calculate, this function will return a Path object (that can be used to
    create the directory)

    Returns:
        pathlib.Path: location somewhere in the user's home directory where to
        put the configs.
    """
    try:
        return Path(appdirs.user_config_dir(prog, org, roaming=True))
    except Exception as ex:
        if default is not RAISE_EXCEPTION:
            logger.debug("Error when trying to find config dir %s", ex, exc_info=True)
            return default
        raise ImpossibleToFindConfigDir() from ex


def config_file(
    name=DEFAULT_CONFIG_FILE, prog=PKG_NAME, org=None, default=RAISE_EXCEPTION
):
    """Finds a file inside :obj:`config_dir`.

    Args:
        name (str): name of the file you are looking for

    The other args are the same as in :obj:`config_dir` and have the same
    meaning.

    Returns:
        pathlib.Path: location of the config file or default if an error
        happenned.
    """
    default_file = default
    if default is not RAISE_EXCEPTION:
        default = None

    dir = config_dir(prog, org, default)
    if dir is None:
        return default_file

    return dir / name
