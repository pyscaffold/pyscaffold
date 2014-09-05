#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import CalledProcessError

import pytest

from pyscaffold import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_Command():
    echo = shell.Command('echo')
    output = echo('Hello Echo!!!')
    assert next(output) == 'Hello Echo!!!'
    output = echo('-e', 'Line1\\\\nLine2\\\\nLine3')
    assert next(output) == 'Line1'
    assert next(output) == 'Line2'
    assert next(output) == 'Line3'
    output = echo('-n', 'No newline')
    assert next(output) == 'No newline'


def test_called_process_error2exit_decorator():
    @shell.called_process_error2exit_decorator
    def func(_):
        raise CalledProcessError(1, "command", "wrong input!")
    with pytest.raises(SystemExit):
        func(1)
