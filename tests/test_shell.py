#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os.path import exists as path_exists

import pytest

from pyscaffold import shell

from .log_helpers import match_last_report


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


def test_shell_command_error2exit_decorator():
    @shell.shell_command_error2exit_decorator
    def func(_):
        shell.ShellCommand('non_existing_cmd')('--wrong-args')

    with pytest.raises(SystemExit):
        func(1)


def test_command_exists():
    assert shell.command_exists('cd')
    assert not shell.command_exists('ldfgyupmqzbch174')


def test_pretend_command(caplog):
    caplog.set_level(logging.INFO)
    # When command runs under pretend flag,
    touch = shell.ShellCommand('touch')
    touch('my-file.txt', pretend=True)
    # then nothing should be executed
    assert not path_exists('my-file.txt')
    # but log should be displayed
    match = match_last_report(caplog)
    assert match['activity'] == 'run'
    assert match['content'] == 'touch my-file.txt'
