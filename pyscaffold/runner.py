# -*- coding: utf-8 -*-
"""
Command-Line-Interface of PyScaffold
"""
from __future__ import absolute_import, print_function

import argparse
import os.path
import sys

import pyscaffold
from six.moves import range

from . import info, repo, shell, structure, templates, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")
    parser.add_argument(
        dest="project",
        help="project name",
        metavar="PROJECT")
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        required=False,
        default=None,
        help="package name (default: project name)",
        metavar="NAME")
    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        required=False,
        default=None,
        help="package description (default: '')",
        metavar="TEXT")
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        default=None,
        help="package url (default: '')",
        metavar="URL")
    license_choices = templates.licenses.keys()
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        required=False,
        default=None,
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
             " like setup.py, _version.py etc. Use additionally --force to "
             "replace all scaffold files.")
    parser.add_argument(
        "--with-namespace",
        dest="namespace",
        default=None,
        help="put your project inside a namespace package",
        metavar="NS1[.NS2]")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--with-cookiecutter",
        dest="cookiecutter_template",
        default=None,
        metavar="TEMPLATE",
        help="additionally apply a cookiecutter template")
    group.add_argument(
        "--with-django",
        dest="django",
        action="store_true",
        default=False,
        help="generate Django project files")
    parser.add_argument(
        "--with-travis",
        dest="travis",
        action="store_true",
        default=False,
        help="generate Travis configuration files")
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
    parser.add_argument(
        "--with-numpydoc",
        dest="numpydoc",
        action="store_true",
        default=False,
        help="add numpydoc to Sphinx configuration file")

    version = pyscaffold.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='PyScaffold {ver}'.format(ver=version))
    opts = parser.parse_args(args)
    if opts.package is None:
        opts.package = utils.make_valid_identifier(opts.project)
    # Strip (back)slash when added accidentally during update
    opts.project = opts.project.rstrip(os.sep)
    # Initialize empty list of all requirements
    utils.safe_set(opts, 'requirements', list())
    return opts


def prepare_namespace(namespace_str):
    """
    Check the validity of namespace_str and split it up into a list

    :param namespace_str: namespace as string, e.g. "com.blue_yonder"
    :return: list of namespaces, e.g. ["com", "com.blue_yonder"]
    """
    namespaces = namespace_str.split('.')
    for namespace in namespaces:
        if not utils.is_valid_identifier(namespace):
            raise RuntimeError(
                "{} is not a valid namespace package.".format(namespace))
    return ['.'.join(namespaces[:i+1]) for i in range(len(namespaces))]


def main(args):
    """
    Main entry point of PyScaffold

    :param args: command line parameters as list of strings
    """
    args = parse_args(args)
    if not info.is_git_installed():
        raise RuntimeError("Make sure git is installed and working.")
    if not info.is_git_configured():
        raise RuntimeError(
            'Make sure git is configured. Run:\n' +
            '  git config --global user.email "you@example.com"\n' +
            '  git config --global user.name "Your Name"\n' +
            "to set your account's default identity.")
    if os.path.exists(args.project):
        if not args.update and not args.force:
            raise RuntimeError(
                "Directory {dir} already exists! Use --update to update an "
                "existing project or --force to overwrite an existing "
                "directory.".format(dir=args.project))
    # Set additional attributes of args
    if args.update:
        args = info.project(args)
    if args.numpydoc:
        utils.safe_set(args, 'numpydoc_sphinx_ext', ", 'numpydoc'")
    if args.namespace:
        args.namespace = prepare_namespace(args.namespace)
    args = structure.set_default_args(args)
    # Apply some preprocessing
    if args.cookiecutter_template:
        structure.create_cookiecutter(args)
    if args.django:
        structure.create_django_proj(args)
        args.requirements.append('django')
    # Convert list of
    proj_struct = structure.make_structure(args)
    structure.create_structure(proj_struct, update=args.update or args.force)
    if args.update and not args.force:
        note = "Please update your setup.cfg according to:\n" \
               "http://pyscaffold.readthedocs.org/en/v{}/configuration.html"
        print(note.format(pyscaffold.__version__))
    if not args.update and not repo.is_git_repo(args.project):
        repo.init_commit_repo(args.project, proj_struct)


@shell.called_process_error2exit_decorator
@utils.exceptions2exit([RuntimeError])
def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
