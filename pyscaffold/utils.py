# -*- coding: utf-8 -*-
"""
Miscellaneous utilities and tools
"""
from __future__ import absolute_import, print_function

import functools
import keyword
import os
import re
import sys
from contextlib import contextmanager
from operator import itemgetter
from distutils.filelist import FileList

from six import PY2

from .templates import licenses


@contextmanager
def chdir(path):
    """Contextmanager to change into a directory

    Args:
        path (str): path to change current working directory to
    """
    curr_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curr_dir)


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
        :obj:`RuntimeError`: raised if identifier can not be converted
    """
    string = string.strip()
    string = string.replace("-", "_")
    string = string.replace(" ", "_")
    string = re.sub('[^_a-zA-Z0-9]', '', string)
    string = string.lower()
    if is_valid_identifier(string):
        return string
    else:
        raise RuntimeError("String cannot be converted to a valid identifier.")


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


def get_files(pattern):
    """Retrieve all files in the current directory by a pattern.

    Use ** as greedy wildcard and * as non-greedy wildcard.

    Args:
        pattern (str): pattern as used by :obj:`distutils.filelist.Filelist`

    Returns:
        [str]: list of files
    """
    filelist = FileList()
    if '**' in pattern:
        pattern = pattern.replace('**', '*')
        anchor = False
    else:
        anchor = True
    filelist.include_pattern(pattern, anchor)
    return filelist.files


def prepare_namespace(namespace_str):
    """Check the validity of namespace_str and split it up into a list

    Args:
        namespace_str (str): namespace, e.g. "com.blue_yonder"

    Returns:
        [str]: list of namespaces, e.g. ["com", "com.blue_yonder"]

    Raises:
          :obj:`RuntimeError` : raised if namespace is not valid
    """
    namespaces = namespace_str.split('.') if namespace_str else list()
    for namespace in namespaces:
        if not is_valid_identifier(namespace):
            raise RuntimeError(
                "{} is not a valid namespace package.".format(namespace))
    return ['.'.join(namespaces[:i+1]) for i in range(len(namespaces))]


def check_setuptools_version():
    """Checks that setuptools has all necessary capabilities for setuptools_scm

    Raises:
          :obj:`RuntimeError` : raised if necessary capabilities are not met
    """
    try:
        from pkg_resources import parse_version, SetuptoolsVersion  # noqa
    except ImportError:
        raise RuntimeError(
            "Your setuptools version is too old (<12).\n"
            "Use `pip install -U setuptools` to upgrade.")
