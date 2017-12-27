# -*- coding: utf-8 -*-
"""
Extension that creates a base structure for the project using django-admin.py.
"""
from __future__ import absolute_import

from .. import shell
from ..api import helpers
from ..api import Extension
from ..contrib.six import raise_from


class Django(Extension):
    """Generate Django project files"""
    mutually_exclusive = True

    def activate(self, actions):
        """Register hooks to generate project using django-admin.

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """

        # `get_default_options` uses passed options to compute derived ones,
        # so it is better to prepend actions that modify options.
        actions = helpers.register(actions, enforce_django_options,
                                   before='get_default_options')
        # `apply_update_rules` uses CWD information,
        # so it is better to prepend actions that modify it.
        actions = helpers.register(actions, create_django_proj,
                                   before='apply_update_rules')

        return actions


def enforce_django_options(struct, opts):
    """Make sure options reflect the Django usage.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    opts['package'] = opts['project']  # required by Django
    opts['force'] = True
    opts.setdefault('requirements', []).append('django')

    return struct, opts


def create_django_proj(struct, opts):
    """Creates a standard Django project with django-admin.py

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        struct, opts: updated project representation and options

    Raises:
        :obj:`RuntimeError`: raised if django-admin.py is not installed
    """
    try:
        shell.django_admin('--version')
    except Exception as e:
        raise raise_from(DjangoAdminNotInstalled, e)

    shell.django_admin('startproject', opts['project'],
                       log=True, pretend=opts.get('pretend'))

    return struct, opts


class DjangoAdminNotInstalled(RuntimeError):
    """This extension depends on the ``django-admin.py`` cli script."""

    DEFAULT_MESSAGE = ("django-admin.py is not installed, "
                       "run: pip install django")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(DjangoAdminNotInstalled, self).__init__(message, *args, **kwargs)
