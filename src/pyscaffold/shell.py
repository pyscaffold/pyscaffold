"""
Shell commands like git, django-admin etc.
"""

import functools
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Union

from .exceptions import ShellCommandException
from .log import logger

PathLike = Union[str, os.PathLike]

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
    """Shell command that can be called with flags like git('add', 'file')

    Args:
        command: command to handle
        shell: run the command in the shell (``True`` by default).
        cwd: current working dir to run the command

    The produced command can be called with the following keyword arguments:

        - **log** (*bool*): log activity when true. ``False`` by default.
        - **pretend** (*bool*): skip execution (but log) when pretending.
          ``False`` by default.

    The positional arguments are passed to the underlying shell command.
    In the case the path to the executable contains spaces of any other special shell
    character, ``command`` needs to be properly quoted.
    """

    def __init__(self, command: str, shell: bool = True, cwd: Optional[str] = None):
        self._command = command
        self._shell = shell
        self._cwd = cwd

    def run(self, *args, **kwargs) -> subprocess.CompletedProcess:
        """Execute command with the given arguments via :obj:`subprocess.run`."""
        command = f"{self._command} {join(args)}".strip()

        should_pretend = kwargs.pop("pretend", False)
        should_log = kwargs.pop("log", should_pretend)
        # ^ When pretending, automatically output logs
        #   (after all, this is the primary purpose of pretending)

        if should_log:
            logger.report("run", command, context=self._cwd)

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
        return subprocess.run(command, **opts)
        # ^ `check_output` does not seem to support terminal editors

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


def get_git_cmd(**args):
    """Retrieve the git shell command depending on the current platform

    Args:
        **args: additional keyword arguments to :obj:`~.ShellCommand`
    """
    if sys.platform == "win32":  # pragma: no cover
        # ^  CI setup does not aggregate Windows coverage
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


def get_executable(
    name: str, prefix: PathLike = sys.prefix, include_path=True
) -> Optional[str]:
    """Find an executable in the system, if available.

    Args:
        name: name of the executable
        prefix: look on this directory, exclusively or in additon to $PATH
            depending on the value of ``include_path``. Defaults to :obj:`sys.prefix`.
        include_path: when True the functions tries to look in the entire $PATH.


    Note:
        The return value might contain whitespaces. If this value is used in a shell
        environment, it needs to be quote properly to avoid the underlying shell
        interpreter splitting the executable path.
    """
    executable = shutil.which(name)
    if include_path and executable:
        return executable

    candidates = list(Path(prefix).resolve().glob(f"*/{name}*"))
    # ^  this works in virtual envs and both Windows and POSIX
    if candidates:
        path = (f.parent for f in sorted(candidates, key=lambda p: len(str(p))))
        return shutil.which(name, path=os.pathsep.join(str(p) for p in path))
        # ^  which will guarantee we find an executable and not only a regular file

    return None


def get_command(
    name: str, prefix: PathLike = sys.prefix, include_path=True, shell=True, **kwargs
) -> Optional[ShellCommand]:
    """Similar to :obj:`get_executable` but return an instance of :obj:`ShellCommand`
    if it is there to be found.
    Additional kwargs will be passed to the :obj:`ShellCommand` constructor.
    """
    executable = get_executable(name, prefix, include_path)
    if not executable:
        return None

    if shell:
        executable = join([executable])

    kwargs["shell"] = shell
    return ShellCommand(executable, **kwargs)


def get_editor(**kwargs):
    """Get an available text editor program"""
    from_env = os.getenv("VISUAL") or os.getenv("EDITOR")
    if from_env:
        return from_env  # user is responsible for proper quoting

    candidates = ((get_executable(e), opts) for e, opts in EDITORS.items())
    editor, opts = next((c for c in candidates if c[0]), (None, [""]))
    if editor:
        return join([editor, *opts])

    msg = "No text editor found in your system, please set EDITOR in your environment"
    raise ShellCommandException(msg)


def edit(file: PathLike, *args, **kwargs) -> Path:
    """Open a text editor and returns back a :obj:`Path` to file, after user editing."""
    editor = ShellCommand(get_editor())
    editor(file, *args, **{"stdout": None, "stderr": None, **kwargs})
    # ^  stdout/stderr=None => required for a terminal editor to open properly
    return Path(file)


def join(parts: Iterable[Union[str, PathLike]]) -> str:
    """Join different parts of a shell command into a string, quoting whitespaces."""
    if sys.platform == "win32":  # pragma: no cover
        # ^  CI setup does not aggregate Windows coverage
        return subprocess.list2cmdline(map(str, parts))

    return " ".join(shlex.quote(str(p)) for p in parts)
    # ^  TODO: Replace with `shlex.join(map(str, parts))` when Python >= 3.8


#: Command for git
git = get_git_cmd()
