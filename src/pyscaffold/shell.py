"""
Interface for external commands and executables like ``git``, ``django-admin`` etc.

Note:
    The naming of this module and its classes refers to ``shell`` for historical
    reasons: prior to PyScaffold v4.0.2, subprocess were spawned using an shell as
    intermediate (i.e. command line interpreter, such as ``/usr/sh`` on POSIX systems).
    The current implementation spawns subprocess directly using operating system calls.
"""
# TODO: Reconsider naming

import functools
import os
import shlex
import shutil
import subprocess
import sys
from itertools import chain
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Union

from .exceptions import ShellCommandException
from .log import logger

PathLike = Union[str, os.PathLike]
IS_POSIX = os.name == "posix"

# The following default flags were borrowed from Github's docs:
# https://docs.github.com/en/github/getting-started-with-github/associating-text-editors-with-git
EDITORS: Dict[str, List[str]] = {
    # -- $EDITOR and $VISUAL should be considered first --
    # Terminal based
    "sensible-editor": [],  # default editor in Debian-based systems like Ubuntu
    "nvim": [],  # if a person has nvim installed, chances are they like it as EDITOR
    "nano": [],  # beginner-friendly, vim users will likely have EDITOR=vim already set
    "vim": [],
    # GUI
    "subl": ["-w"],
    "code": ["--wait"],
    "mate": ["-w"],  # OS X specific
    "atom": ["--wait"],
    # Fallbacks (we tried reasonably hard to find a good editor...)
    "notepad": [],  # Windows
    "vi": [],  # POSIX
}
"""Programs to be tried (in sequence) when calling :obj:`edit` and :obj:`get_editor` in
the case the environment variables EDITOR and VISUAL are not set.
"""


class ShellCommand(object):
    """Wrapper around OS subprocesses with improved API, e.g. ``git('add', 'file')``.

    Args:
        command: command to handle
        shell: run the command in the shell (``False`` by default).
        cwd: current working dir to run the command

    The produced command can be called with the following keyword arguments:

        - **log** (*bool*): log activity when true. ``False`` by default.
        - **pretend** (*bool*): skip execution (but log) when pretending.
          ``False`` by default.

    The positional arguments are passed to the underlying shell command.
    """

    def __init__(self, *command: str, shell: bool = False, cwd: Optional[str] = None):
        self._command = command
        self._shell = shell
        self._cwd = cwd

    def run(self, *args, **kwargs) -> subprocess.CompletedProcess:
        """Execute command with the given arguments via :obj:`subprocess.run`."""
        command = [str(a) for a in chain(self._command, args)]  # Handle Path objects

        should_pretend = kwargs.pop("pretend", False)
        should_log = kwargs.pop("log", should_pretend)
        # ^ When pretending, automatically output logs
        #   (after all, this is the primary purpose of pretending)

        if should_log:
            logger.report("run", " ".join(command), context=self._cwd)
            # ^ TODO: Use shlex.join for Python >= 3.8

        if should_pretend:
            return subprocess.CompletedProcess(command, 0, None, None)

        opts: dict = {
            "shell": self._shell,
            "cwd": self._cwd,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "universal_newlines": True,
            **kwargs,  # allow overwriting defaults
        }
        try:
            return subprocess.run(command, **opts)
            # ^ `check_output` does not seem to support terminal editors
        except FileNotFoundError as ex:
            raise ShellCommandException(str(ex)) from ex

    def __call__(self, *args, **kwargs) -> Iterator[str]:
        """Execute the command, returning an iterator for the resulting text output"""
        completed = self.run(*args, **kwargs)
        try:
            completed.check_returncode()
        except subprocess.CalledProcessError as ex:
            msg = "\n".join(e or "" for e in (completed.stdout, completed.stderr))
            raise ShellCommandException(msg) from ex

        return (line for line in (completed.stdout or "").splitlines())


def shell_command_error2exit_decorator(func: Callable):
    """Decorator to convert given ShellCommandException to an exit message

    This avoids displaying nasty stack traces to end-users
    """

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ShellCommandException as e:
            cause = e.__cause__
            reason = cause.output if cause and hasattr(cause, "output") else e
            print(f"{e}:\n{reason}")
            sys.exit(1)

    return func_wrapper


def get_git_cmd(**kwargs):
    """Retrieve the git shell command depending on the current platform

    Args:
        **kwargs: additional keyword arguments to :obj:`~.ShellCommand`
    """
    if sys.platform == "win32":  # pragma: no cover
        # ^  CI setup does not aggregate Windows coverage
        for cmd in ["git.cmd", "git.exe"]:
            git = ShellCommand(cmd, **kwargs)
            try:
                git("--version")
            except ShellCommandException:
                continue
            return git
        else:
            return None
    else:
        git = ShellCommand("git", **kwargs)
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
    # ^  this works in virtual envs and both Windows and POSIX
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


def get_editor(**kwargs) -> List[str]:
    """Get an available text editor program.

    This function returns a list where the first element is the path to the editor
    executable and the remaining (if any) are default CLI options to be passed.
    """
    from_env = os.getenv("VISUAL") or os.getenv("EDITOR")
    if from_env:
        return shlex.split(from_env, posix=IS_POSIX)

    candidates = ((get_executable(e), opts) for e, opts in EDITORS.items())
    editor, opts = next((c for c in candidates if c[0]), (None, [""]))
    if editor:
        return [editor, *opts]

    msg = "No text editor found in your system, please set EDITOR in your environment"
    raise ShellCommandException(msg)


def edit(file: PathLike, *args, **kwargs) -> Path:
    """Open a text editor and returns back a :obj:`Path` to file, after user editing."""
    editor = ShellCommand(*get_editor())
    editor(file, *args, **{"stdout": None, "stderr": None, **kwargs})
    # ^  stdout/stderr=None => required for a terminal editor to open properly
    return Path(file)


#: Command for git
git = get_git_cmd()
