# -*- coding: utf-8 -*-
"""
Miscellaneous utilities and tools
"""

import errno
import functools
import keyword
import logging
import os
import re
import shutil
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

from pkg_resources import parse_version

from . import __version__ as pyscaffold_version
from .contrib.setuptools_scm.version import VERSION_CLASS
from .exceptions import InvalidIdentifier, OldSetuptools
from .log import logger


@contextmanager
def _chdir_logging_context(path, should_log):
    """Private auxiliar function for logging inside chdir"""
    if should_log:
        logger.report('chdir', path)
        with logger.indent():
            yield
    else:
        yield


@contextmanager
def chdir(path, **kwargs):
    """Contextmanager to change into a directory

    Args:
        path (str): path to change current working directory to

    Keyword Args:
        log (bool): log activity when true. Default: ``False``.
        pretend (bool): skip execution (but log) when pretending.
            Default ``False``.
    """
    should_pretend = kwargs.get('pretend')
    should_log = kwargs.get('log', should_pretend)
    # ^ When pretending, automatically output logs
    #   (after all, this is the primary purpose of pretending)

    curr_dir = os.getcwd()

    try:
        with _chdir_logging_context(path, should_log):
            if not should_pretend:
                # ToDo: Remove str when we require PY 3.6
                os.chdir(str(path))  # str to handle pathlib args
            yield
    finally:
        os.chdir(curr_dir)


def move(*src, **kwargs):
    """Move files or directories to (into) a new location

    Args:
        *src (str[]): one or more files/directories to be moved

    Keyword Args:
        target (str): if target is a directory, ``src`` will be moved inside
            it. Otherwise, it will be the new path (note that it may be
            overwritten)
        log (bool): log activity when true. Default: ``False``.
        pretend (bool): skip execution (but log) when pretending.
            Default ``False``.
    """
    target = kwargs['target']  # Required arg
    should_pretend = kwargs.get('pretend')
    should_log = kwargs.get('log', should_pretend)
    # ^ When pretending, automatically output logs
    #   (after all, this is the primary purpose of pretending)

    for path in src:
        if not should_pretend:
            shutil.move(path, target)
        if should_log:
            logger.report('move', path, target=target)


def is_valid_identifier(string):
    """Check if string is a valid package name

    Args:
        string (str): package name

    Returns:
        bool: True if string is valid package name else False
    """
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
    """Try to make a valid package name identifier from a string

    Args:
        string (str): invalid package name

    Returns:
        str: valid package name as string or :obj:`RuntimeError`

    Raises:
        :obj:`InvalidIdentifier`: raised if identifier can not be converted
    """
    string = string.strip()
    string = string.replace("-", "_")
    string = string.replace(" ", "_")
    string = re.sub('[^_a-zA-Z0-9]', '', string)
    string = string.lower()
    if is_valid_identifier(string):
        return string
    else:
        raise InvalidIdentifier(
                "String cannot be converted to a valid identifier.")


def exceptions2exit(exception_list):
    """Decorator to convert given exceptions to exit messages

    This avoids displaying nasty stack traces to end-users

    Args:
        exception_list [Exception]: list of exceptions to convert
    """
    def exceptions2exit_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except tuple(exception_list) as e:
                if logger.level <= logging.DEBUG:
                    # user surely wants to see the stacktrace
                    traceback.print_exc()
                print("ERROR: {}".format(e))
                sys.exit(1)
        return func_wrapper
    return exceptions2exit_decorator


# from http://en.wikibooks.org/, Creative Commons Attribution-ShareAlike 3.0
def levenshtein(s1, s2):
    """Calculate the Levenshtein distance between two strings

    Args:
        s1 (str): first string
        s2 (str): second string

    Returns:
        int: distance between s1 and s2
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def prepare_namespace(namespace_str):
    """Check the validity of namespace_str and split it up into a list

    Args:
        namespace_str (str): namespace, e.g. "com.blue_yonder"

    Returns:
        [str]: list of namespaces, e.g. ["com", "com.blue_yonder"]

    Raises:
          :obj:`InvalidIdentifier` : raised if namespace is not valid
    """
    namespaces = namespace_str.split('.') if namespace_str else list()
    for namespace in namespaces:
        if not is_valid_identifier(namespace):
            raise InvalidIdentifier(
                "{} is not a valid namespace package.".format(namespace))
    return ['.'.join(namespaces[:i+1]) for i in range(len(namespaces))]


def check_setuptools_version():
    """Check minimum required version of setuptools

    Check that setuptools has all necessary capabilities for setuptools_scm
    as well as support for configuration with the help of ``setup.cfg``.

    Raises:
          :obj:`OldSetuptools` : raised if necessary capabilities are not met
    """
    try:
        from setuptools import __version__ as setuptools_ver
        from pkg_resources import parse_version
    except ImportError:
        raise OldSetuptools

    setuptools_too_old = parse_version(setuptools_ver) < parse_version('38.3')
    setuptools_scm_check_failed = VERSION_CLASS is None
    if setuptools_too_old or setuptools_scm_check_failed:
        raise OldSetuptools


def create_file(path, content, pretend=False):
    """Create a file in the given path.

    This function reports the operation in the logs.

    Args:
        path (str): path in the file system where contents will be written.
        content (str): what will be written.
        pretend (bool): false by default. File is not written when pretending,
            but operation is logged.
    """
    if not pretend:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)

    logger.report('create', path)


def create_directory(path, update=False, pretend=False):
    """Create a directory in the given path.

    This function reports the operation in the logs.

    Args:
        path (str): path in the file system where contents will be written.
        update (bool): false by default. A :obj:`OSError` is raised when update
            is false and the directory already exists.
        pretend (bool): false by default. Directory is not created when
            pretending, but operation is logged.
    """
    if not pretend:
        try:
            os.mkdir(path)
        except OSError:
            if not update:
                raise
            return  # Do not log if not created

    logger.report('create', path)


def dasherize(word):
    """Replace underscores with dashes in the string.

    Example::

        >>> dasherize("foo_bar")
        "foo-bar"

    Args:
        word (str): input word

    Returns:
        input word with underscores replaced by dashes
    """
    return word.replace('_', '-')


def get_id(function):
    """Given a function, calculate its identifier.

    A identifier is a string in the format ``<module name>:<function name>``,
    similarly to the convention used for setuptools entry points.

    Note:
        This function does not return a Python 3 ``__qualname__`` equivalent.
        If the function is nested inside another function or class, the parent
        name is ignored.

    Args:
        function (callable): function object

    Returns:
        str: identifier
    """
    return '{}:{}'.format(function.__module__, function.__name__)


def get_setup_requires_version():
    """Determines the proper `setup_requires` string for PyScaffold

    E.g. setup_requires = pyscaffold>=3.0a0,<3.1a0

    Returns:
        str: requirement string for setup_requires
    """
    require_str = "pyscaffold>={major}.{minor}a0,<{major}.{next_minor}a0"
    major, minor, *rest = (parse_version(pyscaffold_version)
                           .base_version.split('.'))
    next_minor = int(minor) + 1
    return require_str.format(major=major, minor=minor, next_minor=next_minor)


def localize_path(path_string):
    """Localize path for Windows, Unix, i.e. / or \

    Args:
        path_string (str): path using /

    Returns:
        str: path depending on OS
    """
    return str(Path(path_string))


#: Windows-specific error code indicating an invalid pathname.
ERROR_INVALID_NAME = 123


def is_pathname_valid(pathname):
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
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
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
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
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
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def rm_rf(path):
    """Remove a path by all means like `rm -rf` in Linux.

    Args (str): Path to remove:
    """
    shutil.rmtree(path, onerror=on_ro_error)
