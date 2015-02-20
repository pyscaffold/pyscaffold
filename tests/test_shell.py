#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import CalledProcessError

import pytest
from pyscaffold import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_ShellCommand():
    echo = shell.ShellCommand('echo')
    output = echo('Hello Echo!!!')
    assert next(output).strip('"') == 'Hello Echo!!!'
    python = shell.ShellCommand('python')
    output = python('-c', 'print("Hello World")')
    assert list(output)[-1] == 'Hello World'


def test_called_process_error2exit_decorator():
    @shell.called_process_error2exit_decorator
    def func(_):
        raise CalledProcessError(1, "command", "wrong input!")
    with pytest.raises(SystemExit):
        func(1)
