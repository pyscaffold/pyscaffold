#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import choice
from string import ascii_letters
from time import time

from six.moves import xrange


def randstr(n=5):
    """Generates a random string with n ascii_letters"""
    return ''.join(choice(ascii_letters) for _ in xrange(n))


def uniqstr():
    """Generates a random long string that contains random ascii_letters and
    time-based parts.

    The generated strings are meant to be unique, and then can be used to
    identify log entries even if the stream is shared.
    """
    return ''.join(
        randstr() + part
        for part in str(time()).split('.')
    )
