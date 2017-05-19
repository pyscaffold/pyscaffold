# -*- coding: utf-8 -*-
"""
Command-Line-Interface of PyScaffold
"""
from __future__ import absolute_import, print_function

import argparse
import os.path
import sys
from datetime import date

import pyscaffold

from . import info, repo, shell, structure, templates, utils
from .api import Scaffold
from .exceptions import (
    DirectoryAlreadyExists,
    DirectoryDoesNotExist,
    GitNotConfigured,
    GitNotInstalled,
    InvalidIdentifier)
from .extensions import travis

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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--with-cookiecutter",
        dest="cookiecutter_template",
        default="",
        metavar="TEMPLATE",
        help="additionally apply a cookiecutter template")
    group.add_argument(
        "--with-django",
        dest="django",
        action="store_true",
        default=False,
        help="generate Django project files")
    parser.add_argument(
        "--with-pre-commit",
        dest="pre_commit",
        action="store_true",
        default=False,
        help="generate pre-commit configuration file")
    parser.add_argument(
        "--with-tox",
        dest="tox",
        action="store_true",
        default=False,
        help="generate Tox configuration file")

    version = pyscaffold.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='PyScaffold {ver}'.format(ver=version))


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

    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")

    # Make sure entry points are reachable via pkg_resources
    from pkg_resources import iter_entry_points

    # Find all the functions that add arguments to the parser
    cli_extensions = iter_entry_points('pyscaffold.cli')
    parser_extenders = [extension.load() for extension in cli_extensions]

    # Add the arguments to the parser
    for extend in [add_default_args, travis.augment_cli] + parser_extenders:
        extend(parser)

    opts = vars(parser.parse_args(args))
    # Strip (back)slash when added accidentally during update
    opts['project'] = opts['project'].rstrip(os.sep)
    return {k: v for k, v in opts.items() if v is not None}


def _verify_git():
    """Check if git is installed and able to provide the required information.
    """
    if not info.is_git_installed():
        raise GitNotInstalled
    if not info.is_git_configured():
        raise GitNotConfigured


def get_default_opts(project_name, **aux_opts):
    """Creates default options using auxiliary options as keyword argument

    Use this function if you want to use PyScaffold from another application
    in order to generate an option dictionary that can than be passed to
    :obj:`create_project`.

    Args:
        project_name (str): name of the project
        **aux_opts: auxiliary options as keyword parameters

    Returns:
        dict: options with default values set

    Raises:
        :obj:`DirectoryDoesNot` : raised if PyScaffold is told to
            update an inexistent directory
    """

    # This function uses information from git, so make sure it is available
    _verify_git()

    # Merge the default options generated by argparse
    opts = parse_args([project_name])
    # Remove inadvertent double definition of project_name
    aux_opts.pop('project', None)
    opts.update(aux_opts)
    opts.setdefault('package', utils.make_valid_identifier(opts['project']))
    opts.setdefault('author', info.username())
    opts.setdefault('email', info.email())
    opts.setdefault('release_date', date.today().strftime('%Y-%m-%d'))
    opts.setdefault('year', date.today().year)
    opts.setdefault('license', 'none')
    opts.setdefault('description', 'Add a short description here!')
    opts.setdefault('url', 'http://...')
    opts.setdefault('version', pyscaffold.__version__)
    opts.setdefault('title',
                    '='*len(opts['project']) + '\n' + opts['project'] + '\n' +
                    '='*len(opts['project']))
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python']
    opts.setdefault('classifiers', utils.list2str(
        classifiers, indent=4, brackets=False, quotes=False, sep=''))
    opts.setdefault('url', 'http://...')
    # Initialize empty list of all requirements
    opts.setdefault('requirements', list())
    opts['namespace'] = utils.prepare_namespace(opts['namespace'])
    if opts['namespace']:
        opts['root_pkg'] = opts['namespace'][0]
        opts['namespace_pkg'] = ".".join([opts['namespace'][-1],
                                          opts['package']])
    else:
        opts['root_pkg'] = opts['package']
        opts['namespace_pkg'] = opts['package']
    if opts['update']:
        if not os.path.exists(project_name):
            raise DirectoryDoesNotExist(
                "Project {project} does not exist and thus cannot be "
                "updated!".format(project=project_name))
        opts = info.project(opts)
        # Reset project name since the one from setup.cfg might be different
        opts['project'] = project_name
    if opts['django']:
        opts['force'] = True
        opts['package'] = opts['project']  # since this is required by Django
        opts['requirements'].append('django')
    if opts['cookiecutter_template']:
        opts['force'] = True
    return opts


def _init_git(scaffold):
    """Add revision control to the generated files."""
    opts = scaffold.options
    proj_struct = scaffold.filtered_structure
    if not opts['update'] and not repo.is_git_repo(opts['project']):
        repo.init_commit_repo(opts['project'], proj_struct)


def create_project(opts):
    """Create the project's directory structure

    Args:
        opts (dict): options of the project
    """
    _verify_options_consistency(opts)

    if opts['django']:
        structure.create_django_proj(opts)
    if opts['cookiecutter_template']:
        structure.create_cookiecutter(opts)

    scaffold = Scaffold(opts, structure.make_structure(opts),
                        after_generate=[_init_git])

    # Activate the extensions
    extensions = opts.get('extensions', [])
    for extend in extensions:
        extend(scaffold)

    # Call the before_generate hooks
    for hook in scaffold.before_generate:
        hook(scaffold)

    structure.create_structure(scaffold.filtered_structure,
                               update=opts['update'] or opts['force'])

    # Call the before_generate hooks
    for hook in scaffold.after_generate:
        hook(scaffold)


def _verify_options_consistency(opts):
    """Perform some sanity checks about the given options."""
    if os.path.exists(opts['project']):
        if not opts['update'] and not opts['force']:
            raise DirectoryAlreadyExists(
                "Directory {dir} already exists! Use the `update` option to "
                "update an existing project or the `force` option to "
                "overwrite an existing directory.".format(dir=opts['project']))
    if not utils.is_valid_identifier(opts['package']):
        raise InvalidIdentifier(
            "Package name {} is not a valid "
            "identifier.".format(opts['package']))


def main(args):
    """PyScaffold is a tool for putting up the scaffold of a Python project.
    """
    opts = parse_args(args)
    opts = get_default_opts(opts['project'], **opts)
    create_project(opts)
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
