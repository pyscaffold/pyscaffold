# -*- coding: utf-8 -*-
"""
Extension that creates a base structure for the project using django-admin.py.
"""
from __future__ import absolute_import

from .. import shell


def augment_cli(parser):
    """Add an option to parser that enables the Travis extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument(
        "--with-django",
        dest="extensions",
        action="append_const",
        const=extend_project,
        help="generate Django project files")


def extend_project(actions, helpers):
    """Register hooks to generate project using django-admin."""

    register, logger, rpartial = helpers.get('register', 'logger', 'rpartial')

    # `get_default_options` uses passed options to compute derived ones,
    # so it is better to prepend actions that modify options.
    actions = register(actions, enforce_django_options,
                       before='get_default_options')
    # `apply_update_rules` uses CWD information,
    # so it is better to prepend actions that modify it.
    actions = register(actions, rpartial(create_django_proj, logger),
                       before='apply_update_rules')

    return actions


def enforce_django_options(struct, opts):
    """Make sure options reflect the django usage."""
    opts['package'] = opts['project']  # required by Django
    opts['force'] = True
    opts.setdefault('requirements', []).append('django')

    return (struct, opts)


def create_django_proj(struct, opts, logger):
    """Creates a standard Django project with django-admin.py

    Args:
        scaffold (pyscaffold.api.Scaffold): representation of all the actions
        that can be performed by PyScaffold.

    Raises:
        :obj:`RuntimeError`: raised if django-admin.py is not installed
    """
    try:
        shell.django_admin('--version')
    except:
        raise DjangoAdminNotInstalled

    logger.report('run', 'django-admin startproject')
    shell.django_admin('startproject', opts['project'])

    return (struct, opts)


class DjangoAdminNotInstalled(RuntimeError):
    """This extension depends on the ``django-admin.py`` cli script."""

    DEFAULT_MESSAGE = ("django-admin.py is not installed, "
                       "run: pip install django")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(DjangoAdminNotInstalled, self).__init__(message, *args, **kwargs)
