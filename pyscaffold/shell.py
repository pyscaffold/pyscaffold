# -*- coding: utf-8 -*-
"""
Shell commands like git, django-admin.py etc.
"""

from __future__ import absolute_import, division, print_function

import functools
import subprocess
import sys

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


class ShellCommand(object):
    """Shell command that can be called with flags like git('add', 'file')

    Args:
        command (str): command to handle
        shell (bool): run the command in the shell
        cwd (str): current working dir to run the command
    """
    def __init__(self, command, shell=True, cwd=None):
        self._command = command
        self._shell = shell
        self._cwd = cwd

    def __call__(self, *args):
        command = "{cmd} {args}".format(cmd=self._command,
                                        args=subprocess.list2cmdline(args))
        output = subprocess.check_output(command,
                                         shell=self._shell,
                                         cwd=self._cwd,
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        return self._yield_output(output)

    def _yield_output(self, msg):
        for line in msg.splitlines():
            yield line


def called_process_error2exit_decorator(func):
    """Decorator to convert given CalledProcessError to an exit message

    This avoids displaying nasty stack traces to end-users
    """
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            print("{err}:\n{msg}".format(err=str(e), msg=e.output))
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
            except subprocess.CalledProcessError:
                continue
            return git
        return None
    else:
        git = ShellCommand("git", **args)
        try:
            git("--version")
        except subprocess.CalledProcessError:
            return None
        return git


#: Command for git
git = get_git_cmd()

#: Command for django-admin.py
django_admin = ShellCommand("django-admin.py")
