"""
Provide general information about the system, user and the package itself.
"""

import copy
import getpass
import os
import socket
from enum import Enum
from operator import itemgetter
from pathlib import Path
from typing import Optional, Set, cast, overload

import appdirs
from configupdater import ConfigUpdater
from packaging.version import Version

from . import __name__ as PKG_NAME
from . import shell, toml
from .exceptions import (
    ExtensionNotFound,
    GitNotConfigured,
    GitNotInstalled,
    ImpossibleToFindConfigDir,
    PyScaffoldTooOld,
    ShellCommandException,
)
from .file_system import PathLike, chdir
from .identification import deterministic_sort, levenshtein, underscore
from .log import logger
from .templates import ScaffoldOpts, licenses, parse_extensions

CONFIG_FILE = "default.cfg"
"""PyScaffold's own config file name"""

PYPROJECT_TOML: PathLike = "pyproject.toml"
SETUP_CFG: PathLike = "setup.cfg"


class GitEnv(Enum):
    author_name = "GIT_AUTHOR_NAME"
    author_email = "GIT_AUTHOR_EMAIL"
    author_date = "GIT_AUTHOR_DATE"
    committer_name = "GIT_COMMITTER_NAME"
    committer_email = "GIT_COMMITTER_EMAIL"
    committer_date = "GIT_COMMITTER_DATE"


def username() -> str:
    """Retrieve the user's name"""
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


def email() -> str:
    """Retrieve the user's email"""
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
                mail = f"{user}@{host}"
            except Exception as ex:
                logger.debug("Impossible to find user/hostname", exc_info=True)
                raise GitNotConfigured from ex
    return mail


def is_git_installed() -> bool:
    """Check if git is installed"""
    if shell.git is None:
        return False
    try:
        shell.git("--version")
    except ShellCommandException:
        return False
    return True


def is_git_configured() -> bool:
    """Check if user.name and user.email is set globally in git

    Check first git environment variables, then config settings.
    This will also return false if git is not available at all.

    Returns:
        True if it is set globally, False otherwise
    """
    if os.getenv(GitEnv.author_name.value) and os.getenv(GitEnv.author_email.value):
        return True
    else:
        try:
            for attr in ("name", "email"):
                shell.git("config", "--get", f"user.{attr}")
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


def is_git_workspace_clean(path: PathLike) -> bool:
    """Checks if git workspace is clean

    Args:
        path: path to git repository

     Raises:
        :class:`~.GitNotInstalled`: when git command is not available
        :class:`~.GitNotConfigured`: when git does not know user information
    """
    check_git()
    try:
        with chdir(path):
            shell.git("diff-index", "--quiet", "HEAD", "--")
    except ShellCommandException:
        return False
    return True


def project(
    opts: ScaffoldOpts,
    config_path: Optional[PathLike] = None,
    config_file: Optional[PathLike] = None,
) -> ScaffoldOpts:
    """Update user options with the options of an existing config file

    Args:
        opts: options of the project

        config_path: path where config file can be found
            (default: ``opts["project_path"]``)

        config_file: if ``config_path`` is a directory, name of the config file,
            relative to it (default: ``setup.cfg``)

    Returns:
        Options with updated values

    Raises:
        :class:`~.PyScaffoldTooOld`: when PyScaffold is to old to update from
        :class:`~.NoPyScaffoldProject`: when project was not generated with PyScaffold
    """
    # Lazily load the following function to avoid circular dependencies
    from .extensions import NO_LONGER_NEEDED  # TODO: NO_LONGER_SUPPORTED
    from .extensions import list_from_entry_points as list_extensions

    opts = copy.deepcopy({k: v for k, v in opts.items() if not callable(v)})
    # ^  functions/lambdas are not deepcopy-able

    path = config_path or cast(PathLike, opts.get("project_path", "."))

    cfg = read_setupcfg(path, config_file).to_dict()
    if "pyscaffold" not in cfg:
        raise PyScaffoldTooOld

    pyscaffold = cfg.pop("pyscaffold", {})
    metadata = cfg.pop("metadata", {})

    license = metadata.get("license")
    existing = {
        "package": pyscaffold.pop("package", None),
        "name": metadata.get("name"),
        "author": metadata.get("author"),
        "email": metadata.get("author_email") or metadata.get("author-email"),
        "url": metadata.get("url"),
        "description": metadata.get("description", "").strip(),
        "license": license and best_fit_license(license),
    }
    existing = {k: v for k, v in existing.items() if v}  # Filter out non stored values

    # Overwrite only if user has not provided corresponding cli argument
    # Derived/computed parameters should be set by `get_default_options`
    opts = {**existing, **opts}

    # Complement the cli extensions with the ones from configuration
    not_found_ext: Set[str] = set()
    if "extensions" in pyscaffold:
        cfg_extensions = parse_extensions(pyscaffold.pop("extensions", ""))
        opt_extensions = {ext.name for ext in opts.setdefault("extensions", [])}
        add_extensions = cfg_extensions - opt_extensions

        other_ext = list_extensions(filtering=lambda e: e.name in add_extensions)
        not_found_ext = add_extensions - {e.name for e in other_ext} - NO_LONGER_NEEDED
        opts["extensions"] = deterministic_sort(opts["extensions"] + other_ext)

    if not_found_ext:
        raise ExtensionNotFound(list(not_found_ext))

    # TODO: NO_LONGER_SUPPORTED => raise Exception(use older PyScaffold)

    # The remaining values in the pyscaffold section can be added to opts
    # if not specified yet. Useful when extensions define other options.
    for key, value in pyscaffold.items():
        opts.setdefault(key, value)

    return opts


def best_fit_license(txt: Optional[str]) -> str:
    """Finds proper license name for the license defined in txt"""
    corresponding = {
        **{v.replace("license_", ""): k for k, v in licenses.items()},
        **{_simplify_license_name(k): k for k in licenses},
        **{k: k for k in licenses},  # last defined: possibly overwrite
    }
    lic = underscore(txt or list(licenses)[0]).replace("_", "")
    candidates = {underscore(k).replace("_", ""): v for k, v in corresponding.items()}
    ratings = {k: levenshtein(lic.lower(), k.lower()) for k, v in candidates.items()}
    return candidates[min(ratings.items(), key=itemgetter(1))[0]]


def _simplify_license_name(name: str) -> str:
    for term in ("-Clause", "-or-later", "-only"):
        name = name.replace(term, "")
    return name


def read_setupcfg(path: PathLike, filename=SETUP_CFG) -> ConfigUpdater:
    """Reads-in a configuration file that follows a setup.cfg format.
    Useful for retrieving stored information (e.g. during updates)

    Args:
        path: path where to find the config file
        filename: if ``path`` is a directory, ``name`` will be considered a file
            relative to ``path`` to read (default: setup.cfg)

    Returns:
        Object that can be used to read/edit configuration parameters.
    """
    path = Path(path)
    if path.is_dir():
        path = path / (filename or SETUP_CFG)

    updater = ConfigUpdater()
    updater.read(path, encoding="utf-8")

    logger.report("read", path)

    return updater


def read_pyproject(path: PathLike, filename=PYPROJECT_TOML) -> toml.TOMLMapping:
    """Reads-in a configuration file that follows a pyproject.toml format.

    Args:
        path: path where to find the config file
        filename: if ``path`` is a directory, ``name`` will be considered a file
            relative to ``path`` to read (default: setup.cfg)

    Returns:
        Object that can be used to read/edit configuration parameters.
    """
    file = Path(path)
    if file.is_dir():
        file = file / (filename or PYPROJECT_TOML)

    config = toml.loads(file.read_text(encoding="utf-8"))
    logger.report("read", file)
    return config


def get_curr_version(project_path: PathLike):
    """Retrieves the PyScaffold version that put up the scaffold

    Args:
        project_path: path to project

    Returns:
        Version: version specifier
    """
    setupcfg = read_setupcfg(project_path).to_dict()
    return Version(setupcfg["pyscaffold"]["version"])


(RAISE_EXCEPTION,) = list(Enum("default", "RAISE_EXCEPTION"))  # type: ignore
"""When no default value is passed, an exception should be raised"""


@overload
def config_dir(prog: str = PKG_NAME, org: Optional[str] = None) -> Path:
    ...


@overload
def config_dir(
    prog: str = PKG_NAME,
    org: Optional[str] = None,
    default: Optional[Path] = RAISE_EXCEPTION,
) -> Optional[Path]:
    ...


def config_dir(prog=PKG_NAME, org=None, default=RAISE_EXCEPTION):
    """Finds the correct place where to read/write configurations for the given app.

    Args:
        prog: program name (defaults to pyscaffold)
        org: organisation/author name (defaults to the same as ``prog``)
        default: default value to return if an exception was raise while
            trying to find the config dir. If no default value is passed, an
            :obj:`~.ImpossibleToFindConfigDir` execution is raised.

    Please notice even if the directory doesn't exist, if its path is possible
    to calculate, this function will return a Path object (that can be used to
    create the directory)

    Returns:
        Location somewhere in the user's home directory where to put the configs.
    """
    try:
        return Path(appdirs.user_config_dir(prog, org, roaming=True))
    except Exception as ex:
        if default is not RAISE_EXCEPTION:
            logger.debug("Error when trying to find config dir %s", ex, exc_info=True)
            return default
        raise ImpossibleToFindConfigDir() from ex


@overload
def config_file(name: str = CONFIG_FILE, prog: str = PKG_NAME, org: str = None) -> Path:
    ...


@overload
def config_file(
    name: str = CONFIG_FILE,
    prog: str = PKG_NAME,
    org: str = None,
    default: Optional[Path] = RAISE_EXCEPTION,
) -> Optional[Path]:
    ...


def config_file(name=CONFIG_FILE, prog=PKG_NAME, org=None, default=RAISE_EXCEPTION):
    """Finds a file inside :obj:`config_dir`.

    Args:
        name: file you are looking for

    The other args are the same as in :obj:`config_dir` and have the same
    meaning.

    Returns:
        Location of the config file or default if an error happened.
    """
    default_file = default
    if default is not RAISE_EXCEPTION:
        default = None

    dir = config_dir(prog, org, default)
    if dir is None:
        return default_file

    return dir / name
