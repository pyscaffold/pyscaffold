"""
Shell commands like git, django-admin etc.
"""

import functools
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Union

from .exceptions import ShellCommandException
from .log import logger

PathLike = Union[str, os.PathLike]


class ShellCommand(object):
    """Shell command that can be called with flags like git('add', 'file')

    Args:
        command: command to handle
        shell: run the command in the shell
        cwd: current working dir to run the command

    The produced command can be called with the following keyword arguments:

        - **log** (*bool*): log activity when true. ``False`` by default.
        - **pretend** (*bool*): skip execution (but log) when pretending.
          ``False`` by default.

    The positional arguments are passed to the underlying shell command.
    """

    def __init__(self, command: str, shell: bool = True, cwd: Optional[str] = None):
        self._command = command
        self._shell = shell
        self._cwd = cwd

    def __call__(self, *args, **kwargs):
        """Execute command with the given arguments."""
        params = subprocess.list2cmdline(map(str, args))
        command = f"{self._command} {params}"

        should_pretend = kwargs.get("pretend")
        should_log = kwargs.get("log", should_pretend)
        # ^ When pretending, automatically output logs
        #   (after all, this is the primary purpose of pretending)

        if should_log:
            logger.report("run", command, context=self._cwd)

        if should_pretend:
            output = ""
        else:
            try:
                output = subprocess.check_output(
                    command,
                    shell=self._shell,
                    cwd=self._cwd,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )
            except subprocess.CalledProcessError as e:
                raise ShellCommandException(e.output) from e

        return (line for line in output.splitlines())


def shell_command_error2exit_decorator(func: Callable):
    """Decorator to convert given ShellCommandException to an exit message

    This avoids displaying nasty stack traces to end-users
    """

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ShellCommandException as e:
            e = e.__cause__
            print(f"{e}:\n{e.output}")
            sys.exit(1)

    return func_wrapper


def get_git_cmd(**args):
    """Retrieve the git shell command depending on the current platform

    Args:
        **args: additional keyword arguments to :obj:`~.ShellCommand`
    """
    if sys.platform == "win32":
        for cmd in ["git.cmd", "git.exe"]:
            git = ShellCommand(cmd, **args)
            try:
                git("--version")
            except ShellCommandException:
                continue
            return git
        else:
            return None
    else:
        git = ShellCommand("git", **args)
        try:
            git("--version")
        except ShellCommandException:
            return None
        return git


def command_exists(cmd: str) -> bool:
    """Check if command exists

    Args:
        cmd: executable name
    """
    if shutil.which(cmd) is None:
        return False
    else:
        return True


#: Command for git
git = get_git_cmd()


def get_executable(
    name: str, prefix: PathLike = sys.prefix, include_path=True
) -> Optional[str]:
    """Find an executable in the system, if available.

    Args:
        name: name of the executable
        prefix: look on this directory, exclusively or in additon to $PATH
            depending on the value of ``include_path``. Defaults to :obj:`sys.prefix`.
        include_path: when True the functions tries to look in the entire $PATH.
    """
    executable = shutil.which(name)
    if include_path and executable:
        return executable

    candidates = list(Path(prefix).resolve().glob(f"*/{name}*"))
    # ^  this works in virtual envs and both Windows and Posix
    if candidates:
        path = [str(f.parent) for f in sorted(candidates, key=lambda p: len(str(p)))]
        return shutil.which(name, path=os.pathsep.join(path))
        # ^  which will guarantee we find an executable and not only a regular file

    return None


def get_command(
    name: str, prefix: PathLike = sys.prefix, include_path=True, **kwargs
) -> Optional[ShellCommand]:
    """Similar to :obj:`get_executable` but return an instance of :obj:`ShellCommand`
    if it is there to be found.
    Additional kwargs will be passed to the :obj:`ShellCommand` constructor.
    """
    executable = get_executable(name, prefix, include_path)
    return ShellCommand(executable, **kwargs) if executable else None
