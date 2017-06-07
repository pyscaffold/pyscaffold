# -*- coding: utf-8 -*-
"""
Extension that integrates cookiecutter templates into PyScaffold.
"""
from __future__ import absolute_import

import argparse


def augment_cli(parser):
    """Add an option to parser that enables the cookiecutter extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument(
        "--with-cookiecutter",
        dest="cookiecutter_template",
        action=ActivateCookicutter,
        metavar="TEMPLATE",
        help="additionally apply a cookiecutter template")


class ActivateCookicutter(argparse.Action):
    """Consumes the values provided, but also append the extension function
    to the extensions list.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        # First ensure the extension function is stored inside the
        # 'extensions' attribute:
        extensions = getattr(namespace, 'extensions', [])
        extensions.append(extend_project)
        setattr(namespace, 'extensions', extensions)

        # Now the extra parameters can be stored
        setattr(namespace, self.dest, values)


def extend_project(scaffold):
    """Register before_create hooks to generate project using cookiecutter."""

    scaffold.before_generate.insert(0, enforce_cookiecutter_options)
    scaffold.before_generate.append(create_cookiecutter)


def enforce_cookiecutter_options(scaffold):
    """Make sure options reflect the cookiecutter usage."""
    scaffold.options['force'] = True


def create_cookiecutter(scaffold):
    """Create a cookie cutter template

    Args:
        scaffold (pyscaffold.api.Scaffold): representation of all the actions
        that can be performed by PyScaffold.
    """
    try:
        from cookiecutter.main import cookiecutter
    except:
        raise NotInstalled

    opts = scaffold.options  # options of the project
    extra_context = dict(full_name=opts['author'],
                         email=opts['email'],
                         project_name=opts['project'],
                         repo_name=opts['package'],
                         project_short_description=opts['description'],
                         release_date=opts['release_date'],
                         version='unknown',  # will be replaced later
                         year=opts['year'])

    if 'cookiecutter_template' not in opts:
        raise MissingTemplate

    cookiecutter(opts['cookiecutter_template'],
                 no_input=True,
                 extra_context=extra_context)


class NotInstalled(RuntimeError):
    """This extension depends on the ``cookiecutter`` package."""

    DEFAULT_MESSAGE = ("cookiecutter is not installed, "
                       "run: pip install cookiecutter")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(NotInstalled, self).__init__(message, *args, **kwargs)


class MissingTemplate(RuntimeError):
    """A cookiecutter template (git url) is required."""

    DEFAULT_MESSAGE = "missing `cookiecutter_template` option"

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(MissingTemplate, self).__init__(message, *args, **kwargs)
