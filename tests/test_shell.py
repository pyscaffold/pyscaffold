#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from pyscaffold import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_Command():
    echo = shell.Command('echo')
    output = echo('Hello Echo!!!')
    assert next(output) == 'Hello Echo!!!'
