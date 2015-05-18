# -*- coding: utf-8 -*-
"""
Miscellaneous utilities and tools
"""
from __future__ import absolute_import, print_function

import functools
import inspect
import keyword
import os
import re
import sys
from contextlib import contextmanager
from distutils.filelist import FileList

from six import add_metaclass, PY2


@contextmanager
def chdir(path):
    """
    Contextmanager to change into a directory

    :param path: path to change into as string
    """
    curr_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curr_dir)


def is_valid_identifier(string):
    """
    Check if string is a valid package name

    :param string: package name as string
    :return: boolean
    """
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
    """
    Try to make a valid package name identifier from a string

    :param string: invalid package name as string
    :return: valid package name as string or :obj:`RuntimeError`
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


def safe_set(namespace, attr, value):
    """
    Safely set an attribute of a namespace object

    The new attribute is set only if the attribute did not exist or was None.

    :param namespace: namespace as :obj:`argparse.Namespace` object
    :param attr: attribute name as string
    :param value: value for new attribute
    """
    if not hasattr(namespace, attr) or getattr(namespace, attr) is None:
        setattr(namespace, attr, value)


def safe_get(namespace, attr):
    """
    Safely retrieve the value of a namespace's attribute

    :param namespace: namespace as :obj:`argparse.Namespace` object
    :param attr: attribute name as string
    :return: value of the attribute or None
    """
    if hasattr(namespace, attr):
        return getattr(namespace, attr)


def list2str(lst, indent=0, brackets=True, quotes=True):
    """
    Generate a Python syntax list string with an indention

    :param lst: list
    :param indent: indention as integer
    :param brackets: surround the list expression by brackets as boolean
    :param quotes: surround each item with quotes
    :return: string
    """
    if quotes:
        lst_str = str(lst)
        if not brackets:
            lst_str = lst_str[1:-1]
    else:
        lst_str = ', '.join(lst)
        if brackets:
            lst_str = '[' + lst_str + ']'
    lb = ',\n' + indent*' '
    return lst_str.replace(', ', lb)


def exceptions2exit(exception_list):
    """
    Decorator to convert given exceptions to exit messages

    This avoids displaying nasty stack traces to end-users

    :param exception_list: list of exceptions to convert
    """
    def exceptions2exit_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except tuple(exception_list) as e:
                print(e)
                sys.exit(1)
        return func_wrapper
    return exceptions2exit_decorator


class ObjKeeper(type):
    """
    Metaclass to keep track of generated instances of a class
    """
    instances = {}

    def __init__(cls, name, bases, dct):
        cls.instances[cls] = []

    def __call__(cls, *args, **kwargs):
        cls.instances[cls].append(super(ObjKeeper, cls).__call__(*args,
                                                                 **kwargs))
        return cls.instances[cls][-1]


def capture_objs(cls):
    """
    Captures the instances of a given class during runtime

     :param cls: class to capture
     :return: dynamic list with references to all instances of ``cls``
    """
    module = inspect.getmodule(cls)
    name = cls.__name__
    keeper_class = add_metaclass(ObjKeeper)(cls)
    setattr(module, name, keeper_class)
    cls = getattr(module, name)
    return keeper_class.instances[cls]


# from http://en.wikibooks.org/, Creative Commons Attribution-ShareAlike 3.0
def levenshtein(s1, s2):
    """
    Calculate the Levenshtein distance between two strings

    :param s1: first string
    :param s2: second string
    :return: distance between s1 and s2 as integer
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


def utf8_encode(string):
    """
    Encode a Python 2 unicode object to str for compatibility with Python 3

    :param string: Python 2 unicode object or Python 3 str object
    :return: Python 2 str object or Python 3 str object
    """
    return string.encode(encoding='utf8') if PY2 else string


def utf8_decode(string):
    """
    Decode a Python 2 str object to unicode for compatibility with Python 3

    :param string: Python 2 str object or Python 3 str object
    :return: Python 2 unicode object or Python 3 str object
    """
    return string.decode(encoding='utf8') if PY2 else string


def get_files(pattern):
    """
    Retrieve all files in the current directory by a pattern.
    Use ** as greedy wildcard and * as non-greedy wildcard.

    :param pattern: The pattern as used by :obj:`distutils.filelist.Filelist`
    """
    filelist = FileList()
    if '**' in pattern:
        pattern = pattern.replace('**', '*')
        anchor = False
    else:
        anchor = True
    filelist.include_pattern(pattern, anchor)
    return filelist.files
