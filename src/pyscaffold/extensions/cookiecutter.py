# -*- coding: utf-8 -*-
"""
Extension that integrates cookiecutter templates into PyScaffold.

Warning:
    *Deprecation Notice* - In the next major release the Cookiecutter extension
    will be extracted into an independent package.
    After PyScaffold v4.0, you will need to explicitly install
    ``pyscaffoldext-cookiecutter`` in your system/virtualenv in order to be
    able to use it.
"""

import argparse

from ..api import Extension
from ..api.helpers import logger, register
from ..warnings import UpdateNotSupported


class Cookiecutter(Extension):
    """Additionally apply a Cookiecutter template"""
    mutually_exclusive = True

    def augment_cli(self, parser):
        """Add an option to parser that enables the Cookiecutter extension

        Args:
            parser (argparse.ArgumentParser): CLI parser object
        """
        parser.add_argument(
            self.flag,
            dest=self.name,
            action=create_cookiecutter_parser(self),
            metavar="TEMPLATE",
            help="additionally apply a Cookiecutter template. "
                 "Note that not all templates are suitable for PyScaffold. "
                 "Please refer to the docs for more information.")

    def activate(self, actions):
        """Register before_create hooks to generate project using Cookiecutter

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        # `get_default_options` uses passed options to compute derived ones,
        # so it is better to prepend actions that modify options.
        actions = register(actions, enforce_cookiecutter_options,
                           before='get_default_options')

        # `apply_update_rules` uses CWD information,
        # so it is better to prepend actions that modify it.
        actions = register(actions, create_cookiecutter,
                           before='apply_update_rules')

        return actions


def create_cookiecutter_parser(obj_ref):
    """Create a Cookiecutter parser.

    Args:
        obj_ref (Extension): object reference to the actual extension

    Returns:
        NamespaceParser: parser for namespace cli argument
    """
    class CookiecutterParser(argparse.Action):
        """Consumes the values provided, but also append the extension function
        to the extensions list.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            # First ensure the extension function is stored inside the
            # 'extensions' attribute:
            extensions = getattr(namespace, 'extensions', [])
            extensions.append(obj_ref)
            setattr(namespace, 'extensions', extensions)

            # Now the extra parameters can be stored
            setattr(namespace, self.dest, values)

            # save the cookiecutter cli argument for later
            obj_ref.args = values

    return CookiecutterParser


def enforce_cookiecutter_options(struct, opts):
    """Make sure options reflect the cookiecutter usage.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    opts['force'] = True

    return struct, opts


def create_cookiecutter(struct, opts):
    """Create a cookie cutter template

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        struct, opts: updated project representation and options
    """
    if opts.get('update'):
        logger.warning(UpdateNotSupported(extension='cookiecutter'))
        return struct, opts

    try:
        from cookiecutter.main import cookiecutter
    except Exception as e:
        raise NotInstalled from e

    extra_context = dict(full_name=opts['author'],
                         author=opts['author'],
                         email=opts['email'],
                         project_name=opts['project'],
                         package_name=opts['package'],
                         repo_name=opts['package'],
                         project_short_description=opts['description'],
                         release_date=opts['release_date'],
                         version='unknown',  # will be replaced later
                         year=opts['year'])

    if 'cookiecutter' not in opts:
        raise MissingTemplate

    logger.report('run', 'cookiecutter ' + opts['cookiecutter'])
    if not opts.get('pretend'):
        cookiecutter(opts['cookiecutter'],
                     no_input=True,
                     extra_context=extra_context)

    return struct, opts


class NotInstalled(RuntimeError):
    """This extension depends on the ``cookiecutter`` package."""

    DEFAULT_MESSAGE = ("cookiecutter is not installed, "
                       "run: pip install cookiecutter")

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(NotInstalled, self).__init__(message, *args, **kwargs)


class MissingTemplate(RuntimeError):
    """A cookiecutter template (git url) is required."""

    DEFAULT_MESSAGE = "missing `cookiecutter` option"

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(MissingTemplate, self).__init__(message, *args, **kwargs)
