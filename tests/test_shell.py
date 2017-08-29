#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import exists as path_exists
from subprocess import CalledProcessError

import pytest

from pyscaffold import shell

from .log_helpers import match_last_report

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_ShellCommand(tmpfolder):
    echo = shell.ShellCommand('echo')
    output = echo('Hello Echo!!!')
    assert next(output).strip('"') == 'Hello Echo!!!'
    python = shell.ShellCommand('python')
    output = python('-c', 'print("Hello World")')
    assert list(output)[-1] == 'Hello World'
    touch = shell.ShellCommand('touch')
    touch('my-file.txt')
    assert path_exists('my-file.txt')


def test_called_process_error2exit_decorator():
    @shell.called_process_error2exit_decorator
    def func(_):
        raise CalledProcessError(1, "command", "wrong input!")
    with pytest.raises(SystemExit):
        func(1)


def test_command_exists():
    assert shell.command_exists('cd')
    assert not shell.command_exists('ldfgyupmqzbch174')


def test_pretend_command(caplog):
    # When command runs under pretend flag,
    touch = shell.ShellCommand('touch')
    touch('my-file.txt', pretend=True)
    # then nothing should be executed
    assert not path_exists('my-file.txt')
    # but log should be displayed
    match = match_last_report(caplog)
    assert match['activity'] == 'run'
    assert match['content'] == 'touch my-file.txt'
