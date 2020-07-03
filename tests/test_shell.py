# -*- coding: utf-8 -*-
import logging
import re
from os.path import exists as path_exists

import pytest

from pyscaffold import shell

from .helpers import uniqstr


def test_ShellCommand(tmpfolder):
    echo = shell.ShellCommand("echo")
    output = echo("Hello Echo!!!")
    assert next(output).strip('"') == "Hello Echo!!!"
    python = shell.ShellCommand("python")
    output = python("-c", 'print("Hello World")')
    assert list(output)[-1] == "Hello World"
    touch = shell.ShellCommand("touch")
    touch("my-file.txt")
    assert path_exists("my-file.txt")


def test_shell_command_error2exit_decorator():
    @shell.shell_command_error2exit_decorator
    def func(_):
        shell.ShellCommand("non_existing_cmd")("--wrong-args")

    with pytest.raises(SystemExit):
        func(1)


def test_command_exists():
    assert shell.command_exists("tar")
    assert not shell.command_exists("ldfgyupmqzbch174")


def test_pretend_command(caplog):
    caplog.set_level(logging.INFO)
    # When command runs under pretend flag,
    name = uniqstr()
    touch = shell.ShellCommand("touch")
    touch(name, pretend=True)
    # then nothing should be executed
    assert not path_exists(name)
    # but log should be displayed
    logs = caplog.text
    assert re.search(r"run.*touch\s" + name, logs)
