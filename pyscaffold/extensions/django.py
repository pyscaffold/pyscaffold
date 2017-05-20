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


def extend_project(scaffold):
    """Register before_create hooks to generate project using django-admin."""

    scaffold.before_generate.insert(0, enforce_django_options)
    scaffold.before_generate.append(create_django_proj)


def enforce_django_options(scaffold):
    """Make sure options reflect the django usage."""
    opts = scaffold.options  # options of the project
    opts['package'] = opts['project']  # required by Django
    opts['force'] = True
    opts['requirements'].append('django')


def create_django_proj(scaffold):
    """Creates a standard Django project with django-admin.py

    Args:
        scaffold (pyscaffold.api.Scaffold): representation of all the actions
        that can be performed by PyScaffold.

    Raises:
        :obj:`RuntimeError`: raised if django-admin.py is not installed
    """
    opts = scaffold.options  # options of the project
    try:
        shell.django_admin('--version')
    except:
        raise DjangoAdminNotInstalled
    shell.django_admin('startproject', opts['project'])


class DjangoAdminNotInstalled(RuntimeError):
    """This extension depends on the ``django-admin.py`` cli script."""

    DEFAULT_MESSAGE = ("django-admin.py is not installed, "
                       "run: pip install django")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(DjangoAdminNotInstalled, self).__init__(message, *args, **kwargs)
