# -*- coding: utf-8 -*-
"""
Shell commands like git, django-admin.py etc.
"""

from __future__ import print_function, absolute_import, division

import os
import subprocess

import six

# ToDo: Use six.moves when this is available
if six.PY2:
    from pipes import quote
else:
    from shlex import quote

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


class Command(object):
    """
    Shell command that can be called with flags like git('--version')

    :param command: command to handle
    """
    def __init__(self, command):
        self._command = command
        self._output = None

    def __call__(self, *args):
        args = map(quote, args)
        command = "{cmd} {args}".format(cmd=self._command, args=' '.join(args))
        output = subprocess.check_output(command,
                                         shell=True,
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        return self._yield_output(output)

    def _yield_output(self, msg):
        for line in msg.split(os.linesep):
            yield line


def git(*args):
    """
    Command for git

    :param *args: git parameters
    :return: output of git
    """
    return Command("git")(*args)


def django_admin(*args):
    """
    Command for django-admin.py

    :param *args: django-admin.py parameters
    :return: output of django-admin.pu
    """
    return Command("django-admin.py")(*args)
