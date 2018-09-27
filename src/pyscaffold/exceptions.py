# -*- coding: utf-8 -*-
"""
Custom exceptions used by PyScaffold to identify common deviations from the
expected behavior.
"""


class ActionNotFound(KeyError):
    """Impossible to find the required action."""

    def __init__(self, name, *args, **kwargs):
        message = ActionNotFound.__doc__[:-1] + ': `{}`'.format(name)
        super().__init__(message, *args, **kwargs)


class DirectoryAlreadyExists(RuntimeError):
    """The project directory already exists, but no ``update`` or ``force``
    option was used.
    """


class DirectoryDoesNotExist(RuntimeError):
    """No directory was found to be updated."""


class GitNotInstalled(RuntimeError):
    """PyScaffold requires git to run."""

    DEFAULT_MESSAGE = "Make sure git is installed and working."

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class GitNotConfigured(RuntimeError):
    """PyScaffold tries to read user.name and user.email from git config."""

    DEFAULT_MESSAGE = (
        'Make sure git is configured. Run:\n'
        '  git config --global user.email "you@example.com"\n'
        '  git config --global user.name "Your Name"\n'
        "to set your account's default identity.")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class GitDirtyWorkspace(RuntimeError):
    """Workspace of git is empty."""

    DEFAULT_MESSAGE = (
        "Your working tree is dirty. Commit your changes first"
        " or use '--force'.")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class InvalidIdentifier(RuntimeError):
    """Python requires a specific format for its identifiers.

    https://docs.python.org/3.6/reference/lexical_analysis.html#identifiers
    """


class OldSetuptools(RuntimeError):
    """PyScaffold requires a recent version of setuptools."""

    DEFAULT_MESSAGE = (
        "Your setuptools version is too old (<38.3). "
        "Use `pip install -U setuptools` to upgrade.\n"
        "If you have the deprecated `distribute` package installed "
        "remove it or update to version 0.7.3.")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class PyScaffoldTooOld(RuntimeError):
    """PyScaffold cannot update a pre 3.0 version"""

    DEFAULT_MESSAGE = (
        "setup.cfg has no section [pyscaffold]! "
        "Are you trying to update a pre 3.0 version?")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class NoPyScaffoldProject(RuntimeError):
    """PyScaffold cannot update a project that it hasn't generated"""

    DEFAULT_MESSAGE = (
        "Could not update project. Was it generated with PyScaffold?")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ShellCommandException(RuntimeError):
    """Outputs proper logging when a ShellCommand fails"""

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
