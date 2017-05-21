# -*- coding: utf-8 -*-
"""
Command-Line-Interface of PyScaffold
"""
from __future__ import absolute_import, print_function

import argparse
import os.path
import sys

import pyscaffold

from . import api, shell, templates, utils
from .extensions import cookiecutter, django, pre_commit, tox, travis

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


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
        help="package description (default: '')",
        metavar="TEXT")
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        help="package url (default: '')",
        metavar="URL")
    license_choices = templates.licenses.keys()
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        required=False,
        default="none",
        help="package license from {choices} (default: {default})".format(
            choices=str(license_choices), default="No license"),
        metavar="LICENSE")
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
        "--with-namespace",
        dest="namespace",
        default="",
        help="put your project inside a namespace package",
        metavar="NS1[.NS2]")
    version = pyscaffold.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='PyScaffold {ver}'.format(ver=version))


def add_external_generators(parser):
    """Add Django and Cookiecutter in a way they cannot be called together."""
    group = parser.add_mutually_exclusive_group()
    cookiecutter.augment_cli(group)
    django.augment_cli(group)


def parse_args(args):
    """Parse command line parameters

    Args:
        args ([str]): command line parameters as list of strings

    Returns:
        dict: command line parameters
    """

    # `setuptools_scm` (used to determine PyScaffold version) requires features
    # from setuptools not available for old versions, so let's check ...
    utils.check_setuptools_version()

    # Specify the functions that add arguments to the cli
    cli_creators = [
        add_default_args,
        # Built-in extensions:
        add_external_generators,
        travis.augment_cli,
        pre_commit.augment_cli,
        tox.augment_cli]

    # Find any extra function that also do it
    from pkg_resources import iter_entry_points
    cli_extensions = iter_entry_points('pyscaffold.cli')
    cli_extenders = [extension.load() for extension in cli_extensions]

    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")
    parser.set_defaults(extensions=[])

    for augment in cli_creators + cli_extenders:
        augment(parser)

    # Parse options and transform argparse Namespace object into common dict
    opts = vars(parser.parse_args(args))

    # Strip (back)slash when added accidentally during update
    opts['project'] = opts['project'].rstrip(os.sep)

    # Remove options with None values
    return {k: v for k, v in opts.items() if v is not None}


def main(args):
    """PyScaffold is a tool for putting up the scaffold of a Python project.
    """
    opts = parse_args(args)
    opts = api.get_default_opts(opts['project'], **opts)
    api.create_project(opts)
    if opts['update'] and not opts['force']:
        note = "Update accomplished!\n" \
               "Please check if your setup.cfg still complies with:\n" \
               "http://pyscaffold.readthedocs.org/en/v{}/configuration.html"
        print(note.format(pyscaffold.__version__))


@shell.called_process_error2exit_decorator
@utils.exceptions2exit([RuntimeError])
def run():
    """Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
