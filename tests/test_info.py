#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import info

import pytest

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_username():
    username = info.username()
    print(type(username))
    assert isinstance(username, str)
    assert len(username) > 0


def test_email():
    email = info.email()
    assert "@" in email
