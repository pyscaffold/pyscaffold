# -*- coding: utf-8 -*-
"""
Command-Line-Interface of PyScaffold
"""

import argparse
import logging
import os.path
import sys

from pkg_resources import parse_version

from . import __version__ as pyscaffold_version
from . import api, info, shell, templates, utils
from .exceptions import NoPyScaffoldProject
from .log import ReportFormatter, configure_logger
from .utils import get_id


def add_default_args(parser):
    """Add the default options and arguments to the CLI parser.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """

    parser.add_argument(
        dest="project",
        help="project name",
        metavar="PROJECT")
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        required=False,
        help="package name (default: project name)",
        metavar="NAME")
    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        required=False,
        help="package description",
        metavar="TEXT")
    license_choices = templates.licenses.keys()
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        required=False,
        default="mit",
        help="package license like {choices} (default: {default})".format(
            choices=', '.join(license_choices), default="mit"),
        metavar="LICENSE")
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        help="package url",
        metavar="URL")
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="force overwriting an existing directory")
    parser.add_argument(
        "-U",
        "--update",
        dest="update",
        action="store_true",
        default=False,
        help="update an existing project by replacing the most important files"
             " like setup.py etc. Use additionally --force to "
             "replace all scaffold files.")
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='PyScaffold {ver}'.format(ver=pyscaffold_version))
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="log_level",
        help="show additional information about current actions")
    parser.add_argument(
        "-vv",
        "--very-verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="show all available information about current actions")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-P",
        "--pretend",
        dest="pretend",
        action="store_true",
        default=False,
        help="do not create project, but displays the log of all operations"
             " as if it had been created.")
    group.add_argument(
        "--list-actions",
        dest="command",
        action="store_const",
        const=list_actions,
        help="do not create project, but show a list of planned actions")


def parse_args(args):
    """Parse command line parameters respecting extensions

    Args:
        args ([str]): command line parameters as list of strings

    Returns:
        dict: command line parameters
    """
    from pkg_resources import iter_entry_points

    # create the argument parser
    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")
    parser.set_defaults(log_level=logging.WARNING,
                        extensions=[],
                        command=run_scaffold)
    add_default_args(parser)
    # load and instantiate extensions
    cli_extensions = [extension.load()(extension.name) for extension
                      in iter_entry_points('pyscaffold.cli')]
    # add a group for mutually exclusive external generators
    mutex_group = parser.add_mutually_exclusive_group()
    for extension in cli_extensions:
        if extension.mutually_exclusive:
            extension.augment_cli(mutex_group)
        else:
            extension.augment_cli(parser)

    # Parse options and transform argparse Namespace object into common dict
    opts = vars(parser.parse_args(args))
    return opts


def process_opts(opts):
    """Process and enrich command line arguments

    Args:
        opts (dict): dictionary of parameters

    Returns:
        dict: dictionary of parameters from command line arguments
    """
    # When pretending the user surely wants to see the output
    if opts['pretend']:
        opts['log_level'] = logging.INFO

    configure_logger(opts)

    # In case of an update read and parse setup.cfg
    if opts['update']:
        try:
            opts = info.project(opts)
        except Exception as e:
            raise NoPyScaffoldProject from e

    # Save cli params for later updating
    opts['cli_params'] = {'extensions': list(), 'args': dict()}
    for extension in opts['extensions']:
        opts['cli_params']['extensions'].append(extension.name)
        if extension.args is not None:
            opts['cli_params']['args'][extension.name] = extension.args

    # Strip (back)slash when added accidentally during update
    opts['project'] = opts['project'].rstrip(os.sep)

    # Remove options with None values
    opts = {k: v for k, v in opts.items() if v is not None}
    return opts


def run_scaffold(opts):
    """Actually scaffold the project, calling the python API

    Args:
        opts (dict): command line options as dictionary
    """
    api.create_project(opts)
    if opts['update'] and not opts['force']:
        note = "Update accomplished!\n" \
               "Please check if your setup.cfg still complies with:\n" \
               "https://pyscaffold.org/en/v{}/configuration.html"
        base_version = parse_version(pyscaffold_version).base_version
        print(note.format(base_version))


def list_actions(opts):
    """Do not create a project, just list actions considering extensions

    Args:
        opts (dict): command line options as dictionary
    """
    actions = api.discover_actions(opts.get('extensions', []))

    print('Planned Actions:')
    for action in actions:
        print(ReportFormatter.SPACING + get_id(action))


def main(args):
    """Main entry point for external applications

    Args:
        args ([str]): command line arguments
    """
    utils.check_setuptools_version()
    opts = parse_args(args)
    opts = process_opts(opts)
    opts['command'](opts)


@shell.shell_command_error2exit_decorator
@utils.exceptions2exit([RuntimeError])
def run():
    """Entry point for console script"""
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
