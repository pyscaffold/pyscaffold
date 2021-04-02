import logging
import os
import re
import shlex
import shutil
import stat
import sys
from pathlib import Path
from pprint import pformat

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
    assert Path("my-file.txt").exists()


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
    assert not Path(name).exists()
    # but log should be displayed
    logs = caplog.text
    assert re.search(r"run.*touch\s" + name, logs)


def test_get_executable(tmpfolder):
    # Some python should exist
    assert shell.get_executable("python") is not None
    # No python should exist in an empty directory when the global $PATH is not included
    assert shell.get_executable("python", tmpfolder, include_path=False) is None
    # When using sys.prefix python should be sys.executable (+ version suffix)
    python = Path(sys.executable).resolve()
    bin_path = shell.get_executable("python", include_path=False, prefix=sys.prefix)
    bin_path = Path(bin_path).resolve()
    assert bin_path.stem in python.stem
    assert bin_path.parent == python.parent
    # Non existing binaries => None
    assert shell.get_executable(uniqstr()) is None


def test_get_command():
    python = shell.get_command("python", prefix=sys.prefix, include_path=False)
    assert next(python("--version")).strip().startswith("Python 3")
    with pytest.raises(shell.ShellCommandException):
        python("--" + uniqstr())


def test_get_command_inexistent():
    name = uniqstr()
    inexistent = shell.get_command(name, prefix=sys.prefix, include_path=False)
    assert inexistent is None


def test_get_command_with_whitespace(tmpfolder):
    # Given an executable exists in a path with spaces
    prefix = Path(tmpfolder, "with spaces")
    if os.name == "posix":
        executable = Path(prefix, "bin", "myexec")
        executable.parent.mkdir(parents=True, exist_ok=True)
        executable.write_text("#!/bin/sh\n\necho 42")
        executable.chmod(stat.S_IMODE(stat.S_IREAD | stat.S_IEXEC))
    elif os.name == "nt":  # Windows
        executable = Path(prefix, "Script", "myexec.bat")
        executable.parent.mkdir(parents=True, exist_ok=True)
        executable.write_text("@echo off\r\necho 42", encoding="ascii")
        # ^  Let's use a basic encoding + CRLF for windows
    else:
        pytest.skip("Requires either POSIX-compliant OS or Windows")
        return

    # ----> helps when debugging
    exec_path = shell.get_executable("myexec", prefix=prefix, include_path=False)
    print("exec_path:", pformat(shlex.quote(exec_path)))
    print("contents:\n", pformat(executable.read_text()))
    assert exec_path is not None
    assert Path(exec_path).exists()
    # <----

    # When we create a command with `get_command`
    cmd = shell.get_command("myexec", prefix=prefix, include_path=False)
    assert cmd is not None
    # it should run without any problems
    completed = cmd.run()
    print("stdout:", completed.stdout)
    assert int(completed.stdout) == 42
    completed.check_returncode()


def test_get_editor(monkeypatch):
    # In general we should always find an editor
    assert shell.get_editor() is not None
    # When there is a problem, then we should have a nice error message
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "")
    monkeypatch.setattr(shell, "get_executable", lambda *_, **__: None)
    with pytest.raises(shell.ShellCommandException, match="set EDITOR"):
        print("editor", shell.get_editor())


def test_edit(tmpfolder, monkeypatch):
    vi = shutil.which("vim") or shutil.which("vi")
    if not vi:
        pytest.skip("This test requires `vim` or `vi` to be available")

    # Given a file exists
    file = tmpfolder / "test.txt"
    file.write_text("Hello World", "utf-8")
    assert file.read_text("utf-8").strip() == "Hello World"

    # Then `shell.edit` should be able to manipulate it
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", vi)
    shell.edit(file, "-c", ":%s/World/PyScaffold/g", "-c", ":wq")
    # ^ a bit of vim scripting so it does not wait for the user to type

    assert file.read_text("utf-8").strip() == "Hello PyScaffold"


def test_join():
    # Join should work with empty iterables
    assert shell.join([]) == ""
    assert shell.join({}) == ""
    assert shell.join(()) == ""
    assert shell.join(x for x in []) == ""

    # Join should accept Path objects
    p1 = Path("a", "b", "c")
    p2 = Path("d", "f", "g")
    assert shell.join([p1, p2]) == f"{p1} {p2}"

    # Join should be the opposite of split
    args = ["/my path/to exec", '"other args"', "asdf", "42", "'a b c'"]
    assert shlex.split(shell.join(args)) == args
