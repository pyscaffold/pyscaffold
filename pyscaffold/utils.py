# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import re
import sys
import contextlib
import inspect
import keyword
import functools

from six import add_metaclass


@contextlib.contextmanager
def chdir(path):
    curr_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(curr_dir)


def is_valid_identifier(string):
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
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
    if not hasattr(namespace, attr) or getattr(namespace, attr) is None:
        setattr(namespace, attr, value)


def safe_get(namespace, attr):
    if hasattr(namespace, attr):
        return getattr(namespace, attr)


def list2str(lst, indent=0):
    lst_str = str(lst)
    lb = ',\n' + indent*' '
    return lst_str.replace(', ', lb)


def exceptions2exit(exception_list):
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
    instances = {}

    def __init__(cls, name, bases, dct):
        cls.instances[cls] = []

    def __call__(cls, *args, **kwargs):
        cls.instances[cls].append(super(ObjKeeper, cls).__call__(*args,
                                                                 **kwargs))
        return cls.instances[cls][-1]


def capture_objs(cls):
    module = inspect.getmodule(cls)
    name = cls.__name__
    keeper_class = add_metaclass(ObjKeeper)(cls)
    setattr(module, name, keeper_class)
    cls = getattr(module, name)
    return keeper_class.instances[cls]


def git2pep440(ver_str):
    dash_count = ver_str.count('-')
    if dash_count == 0:
        return ver_str
    elif dash_count == 1:
        return ver_str.split('-')[0] + ".post.dev1.pre"
    elif dash_count == 2:
        tag, commits, _ = ver_str.split('-')
        return ".post.dev".join([tag, commits])
    elif dash_count == 3:
        tag, commits, _, _ = ver_str.split('-')
        commits = str(int(commits) + 1)
        return ".post.dev".join([tag, commits]) + ".pre"
    else:
        raise RuntimeError("Invalid version string")
