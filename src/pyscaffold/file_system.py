"""Internal library that encapsulate file system manipulation.
Examples include: creating/removing files and directories, changing permissions, etc.

Functions in this library usually extend the behaviour of Python's standard lib by
providing proper error handling or adequate logging/control flow in the context of
PyScaffold (an example of adequate control flow logic is dealing with the ``pretend``
flag).
"""

import errno
import os
import shutil
import stat
import sys
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from tempfile import mkstemp
from typing import Callable, Optional, Union

from .log import logger

PathLike = Union[str, os.PathLike]


@contextmanager
def tmpfile(**kwargs):
    """Context manager that yields a temporary :obj:`Path`"""
    fp, path = mkstemp(**kwargs)
    os.close(fp)  # we don't need the low level file handler
    file = Path(path)
    try:
        yield file
    finally:
        file.unlink()


@contextmanager
def _chdir_logging_context(path: PathLike, should_log: bool):
    """Private auxiliar function for logging inside chdir"""
    if should_log:
        logger.report("chdir", path)
        with logger.indent():
            yield
    else:
        yield


@contextmanager
def chdir(path: PathLike, **kwargs):
    """Contextmanager to change into a directory

    Args:
        path : path to change current working directory to

    Keyword Args:
        log (bool): log activity when true. Default: ``False``.
        pretend (bool): skip execution (but log) when pretending.
            Default ``False``.
    """
    should_pretend = kwargs.get("pretend")
    should_log = kwargs.get("log", should_pretend)
    # ^ When pretending, automatically output logs
    #   (after all, this is the primary purpose of pretending)

    curr_dir = os.getcwd()

    try:
        with _chdir_logging_context(path, should_log):
            if not should_pretend:
                os.chdir(path)
            yield
    finally:
        os.chdir(curr_dir)


def move(*src: PathLike, target: PathLike, **kwargs):
    """Move files or directories to (into) a new location

    Args:
        *src (PathLike): one or more files/directories to be moved

    Keyword Args:
        target (PathLike): if target is a directory, ``src`` will be
            moved inside it. Otherwise, it will be the new path (note that it
            may be overwritten)
        log (bool): log activity when true. Default: ``False``.
        pretend (bool): skip execution (but log) when pretending.
            Default ``False``.
    """
    should_pretend = kwargs.get("pretend")
    should_log = kwargs.get("log", should_pretend)
    # ^ When pretending, automatically output logs
    #   (after all, this is the primary purpose of pretending)

    for path in src:
        if not should_pretend:
            shutil.move(str(path), str(target))
        if should_log:
            logger.report("move", path, target=target)


def create_file(path: PathLike, content: str, pretend=False, encoding="utf-8"):
    """Create a file in the given path.

    This function reports the operation in the logs.

    Args:
        path: path in the file system where contents will be written.
        content: what will be written.
        pretend (bool): false by default. File is not written when pretending,
            but operation is logged.

    Returns:
        Path: given path
    """
    path = Path(path)
    if not pretend:
        path.write_text(content, encoding=encoding)

    logger.report("create", path)
    return path


def create_directory(path: PathLike, update=False, pretend=False) -> Optional[Path]:
    """Create a directory in the given path.

    This function reports the operation in the logs.

    Args:
        path: path in the file system where contents will be written.
        update (bool): false by default. A :obj:`OSError` can be raised
            when update is false and the directory already exists.
        pretend (bool): false by default. Directory is not created when
            pretending, but operation is logged.
    """
    path = Path(path)
    if path.is_dir() and update:
        logger.report("skip", path)
        return None

    if not pretend:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            if not update:
                raise
            return path  # Do not log if not created

    logger.report("create", path)
    return path


def chmod(path: PathLike, mode: int, pretend=False) -> Path:
    """Change the permissions of file in the given path.

    This function reports the operation in the logs.

    Args:
        path: path in the file system whose permissions will be changed
        mode: new permissions, should be a combination of
            :obj`stat.S_* <stat.S_IXUSR>` (see :obj:`os.chmod`).
        pretend (bool): false by default. File is not changed when pretending,
            but operation is logged.
    """
    path = Path(path)
    mode = stat.S_IMODE(mode)

    if not pretend:
        path.chmod(mode)

    logger.report("chmod {:03o}".format(mode), path)
    return path


def localize_path(path_string: str) -> str:
    """Localize path for Windows, Unix, i.e. / or \\

    Args:
        path_string (str): path using /

    Returns:
        str: path depending on OS
    """
    return str(Path(path_string))


#: Windows-specific error code indicating an invalid pathname.
ERROR_INVALID_NAME = 123


def is_pathname_valid(pathname: str) -> bool:
    """Check if a pathname is valid

    Code by Cecil Curry from StackOverflow

    Args:
        pathname (str): string to validate

    Returns:
        `True` if the passed pathname is a valid pathname for the current OS;
        `False` otherwise.
    """
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = (
            os.environ.get("HOMEDRIVE", "C:")
            if sys.platform == "win32"
            else os.path.sep
        )
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, "winerror"):
                    if exc.winerror == ERROR_INVALID_NAME:  # type: ignore
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


def on_ro_error(func, path, exc_info):
    """Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``

    Args:
        func (callable): function which raised the exception
        path (str): path passed to `func`
        exc_info (tuple of str): exception info returned by sys.exc_info()
    """
    import stat
    from time import sleep

    # Sometimes the SO is just asynchronously (??!) slow, but it does remove the file
    sleep(0.5)

    if not Path(path).exists():
        return

    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        return func(path)

    raise


def rm_rf(path: PathLike, pretend=False):
    """Remove ``path`` by all means like ``rm -rf`` in Linux"""
    target = Path(path)
    if not target.exists():
        return None

    if target.is_dir():
        remove: Callable = partial(shutil.rmtree, onerror=on_ro_error)
    else:
        remove = Path.unlink

    if not pretend:
        remove(target)

    logger.report("remove", target)
    return path
