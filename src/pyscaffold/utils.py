# -*- coding: utf-8 -*-
"""
Miscellaneous utilities and tools
"""
from __future__ import absolute_import, print_function

import functools
import keyword
import os
import re
import shutil
import sys
from contextlib import contextmanager
from operator import itemgetter

from .exceptions import InvalidIdentifier, OldSetuptools
from .log import logger
from .templates import licenses
from .contrib.six import PY2
from .contrib.setuptools_scm.version import VERSION_CLASS


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
    if not should_pretend:
        os.chdir(path)

    try:
        if should_log:
            logger.report('chdir', path)
            with logger.indent():
                yield
        else:
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


def list2str(lst, indent=0, brackets=True, quotes=True, sep=','):
    """Generate a Python syntax list string with an indention

    Args:
        lst ([str]): list of strings
        indent (int): indention
        brackets (bool): surround the list expression by brackets
        quotes (bool): surround each item with quotes
        sep (str): separator for each item

    Returns:
        str: string representation of the list
    """
    if quotes:
        lst_str = str(lst)
        if not brackets:
            lst_str = lst_str[1:-1]
    else:
        lst_str = ', '.join(lst)
        if brackets:
            lst_str = '[' + lst_str + ']'
    lb = '{}\n'.format(sep) + indent*' '
    return lst_str.replace(', ', lb)


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


def best_fit_license(txt):
    """Finds proper license name for the license defined in txt

    Args:
        txt (str): license name

    Returns:
        str: license name
    """
    ratings = {lic: levenshtein(txt, lic.lower()) for lic in licenses}
    return min(ratings.items(), key=itemgetter(1))[0]


def utf8_encode(string):
    """Encode a Python 2 unicode object to str for compatibility with Python 3

    Args:
        string (str): Python 2 unicode object or Python 3 str object

    Returns:
        str: Python 2 str object or Python 3 str object
    """
    return string.encode(encoding='utf8') if PY2 else string


def utf8_decode(string):
    """Decode a Python 2 str object to unicode for compatibility with Python 3

    Args:
        string (str): Python 2 str object or Python 3 str object

    Returns:
        str: Python 2 unicode object or Python 3 str object
    """
    return string.decode(encoding='utf8') if PY2 else string


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
        from distutils.version import LooseVersion
        from setuptools import __version__ as setuptools_ver
    except ImportError:
        raise OldSetuptools

    # ToDo: Stop due to bug https://github.com/pypa/setuptools/issues/1136
    from .contrib.six import PY2
    if PY2:
        raise RuntimeError(
            "Due to a bug in setuptools, PyScaffold currently needs at least "
            "Python 3.4! Install PyScaffold 2.5 for Python 2.7 support.")

    setuptools_too_old = LooseVersion(setuptools_ver) < LooseVersion('30.3.0')
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
        with open(path, 'w') as fh:
            fh.write(utf8_encode(content))

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
