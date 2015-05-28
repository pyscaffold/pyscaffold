# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""
from __future__ import absolute_import, print_function

import copy
import os
from datetime import date
from os.path import join as join_path

import pyscaffold
from six import string_types

from . import info, shell, templates, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


class FileOp(object):
    """
    Namespace for file operations during an update

    NO_OVERWRITE: Do not overwrite an existing file during update
    NO_CREATE: Do not create the file during an update
    """
    NO_OVERWRITE = 0
    NO_CREATE = 1


def set_default_args(args):
    """
    Set default arguments for some parameters

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    args = copy.copy(args)
    utils.safe_set(args, "author", info.username())
    utils.safe_set(args, "email", info.email())
    utils.safe_set(args, "release_date", date.today().strftime('%Y-%m-%d'))
    utils.safe_set(args, "year", date.today().year)
    utils.safe_set(args, "license", "none")
    utils.safe_set(args, "description", "Add a short description here!")
    utils.safe_set(args, "url", "http://...")
    utils.safe_set(args, "version", pyscaffold.__version__)
    utils.safe_set(args, "title", "="*len(args.project) + "\n" +
                                  args.project + "\n" +
                                  "="*len(args.project))
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python']
    utils.safe_set(args, "classifiers", utils.list2str(classifiers,
                                                       indent=14,
                                                       brackets=False,
                                                       quotes=False))
    utils.safe_set(args, "console_scripts", "")
    utils.safe_set(args, "numpydoc_sphinx_ext", "")
    utils.safe_set(args, "namespace", list())
    return args


def add_namespace(args, struct):
    """
    Prepend the namespace to a given file structure

    :param args: command line parameters as :obj:`argparse.Namespace`
    :param struct: directory structure as dictionary of dictionaries
    :return: directory structure as dictionary of dictionaries
    """
    if not args.namespace:
        return struct
    namespace = args.namespace[-1].split(".")
    base_struct = struct
    pkg_struct = struct[args.project][args.package]
    struct = base_struct[args.project]
    del struct[args.package]
    for sub_package in namespace:
        struct[sub_package] = {"__init__.py": templates.namespace(args)}
        struct = struct[sub_package]
    struct[args.package] = pkg_struct
    return base_struct


def make_structure(args):
    """
    Creates the project structure as dictionary of dictionaries

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: structure as dictionary of dictionaries
    """
    struct = {args.project: {
        ".gitignore": templates.gitignore(args),
        args.package: {"__init__.py": templates.init(args),
                       "skeleton.py": templates.skeleton(args)},
        "tests": {"conftest.py": templates.conftest_py(args)},
        "docs": {"conf.py": templates.sphinx_conf(args),
                 "authors.rst": templates.sphinx_authors(args),
                 "index.rst": templates.sphinx_index(args),
                 "license.rst": templates.sphinx_license(args),
                 "changes.rst": templates.sphinx_changes(args),
                 "Makefile": templates.sphinx_makefile(args),
                 "_static": {
                     ".gitignore": templates.gitignore_empty(args)}},
        "README.rst": templates.readme(args),
        "AUTHORS.rst": templates.authors(args),
        "LICENSE.txt": templates.license(args),
        "CHANGES.rst": templates.changes(args),
        "setup.py": templates.setup_py(args),
        "setup.cfg": templates.setup_cfg(args),
        "requirements.txt": templates.requirements(args),
        ".coveragerc": templates.coveragerc(args)}}
    proj_dir = struct[args.project]
    if args.travis:
        proj_dir[".travis.yml"] = templates.travis(args)
        proj_dir["tests"]["travis_install.sh"] = templates.travis_install(args)
    if args.django:
        proj_dir["manage.py"] = None
        proj_dir[args.package]["settings.py"] = None
        proj_dir[args.package]["urls.py"] = None
        proj_dir[args.package]["wsgi.py"] = None
    if args.pre_commit:
        proj_dir[".pre-commit-config.yaml"] = templates.pre_commit_config(args)
    if args.tox:
        proj_dir["tox.ini"] = templates.tox(args)
    if args.update and not args.force:  # Do not overwrite following files
        rules = {args.project: {
            ".gitignore": FileOp.NO_OVERWRITE,
            ".gitattributes": FileOp.NO_OVERWRITE,
            "setup.cfg": FileOp.NO_OVERWRITE,
            "README.rst": FileOp.NO_OVERWRITE,
            "CHANGES.rst": FileOp.NO_OVERWRITE,
            "LICENSE.txt": FileOp.NO_OVERWRITE,
            "AUTHORS.rst": FileOp.NO_OVERWRITE,
            "requirements.txt": FileOp.NO_OVERWRITE,
            ".travis.yml": FileOp.NO_OVERWRITE,
            ".coveragerc": FileOp.NO_OVERWRITE,
            ".pre-commit-config.yaml": FileOp.NO_OVERWRITE,
            "tox.ini": FileOp.NO_OVERWRITE,
            args.package: {"skeleton.py": FileOp.NO_CREATE},
            "tests": {"conftest.py": FileOp.NO_OVERWRITE,
                      "travis_install.sh": FileOp.NO_OVERWRITE},
            "docs": {"index.rst": FileOp.NO_OVERWRITE}
        }}
        struct = apply_update_rules(rules, struct)
    struct = add_namespace(args, struct)

    return struct


def create_structure(struct, prefix=None, update=False):
    """
    Manifests a directory structure in the filesystem

    :param struct: directory structure as dictionary of dictionaries
    :param prefix: prefix path for the structure
    :param update: update an existing directory structure as boolean
    """
    if prefix is None:
        prefix = os.getcwd()
    for name, content in struct.items():
        if isinstance(content, string_types):
            with open(join_path(prefix, name), "w") as fh:
                fh.write(utils.utf8_encode(content))
        elif isinstance(content, dict):
            try:
                os.mkdir(join_path(prefix, name))
            except OSError:
                if not update:
                    raise
            create_structure(struct[name],
                             prefix=join_path(prefix, name),
                             update=update)
        elif content is None:
            pass
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))


def create_django_proj(args):
    """
    Creates a standard Django project with django-admin.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    """
    try:
        shell.django_admin("--version")
    except:
        raise RuntimeError("django-admin.py is not installed, "
                           "run: pip install django")
    shell.django_admin("startproject", args.project)
    args.package = args.project  # since this is required by Django
    args.force = True


def create_cookiecutter(args):
    """
    Create a cookie cutter template

    :param args: command line parameters as :obj:`argparse.Namespace`
    """
    try:
        from cookiecutter.main import cookiecutter
    except:
        raise RuntimeError("cookiecutter is not installed, "
                           "run: pip install cookiecutter")
    extra_context = dict(full_name=args.author,
                         email=args.email,
                         project_name=args.project,
                         repo_name=args.package,
                         project_short_description=args.description,
                         release_date=args.release_date,
                         version='unknown',  # will be replaced later
                         year=args.year)

    cookiecutter(args.cookiecutter_template,
                 no_input=True,
                 extra_context=extra_context)
    args.force = True


def apply_update_rules(rules, struct, prefix=None):
    """
    Apply update rules using :obj:`~.FileOp` to a directory structure

    :param rules: directory structure as dictionary of dictionaries with
        :obj:`~.FileOp` keys. The structure will be modified.
    :param struct: directory structure as dictionary of dictionaries
    :param prefix: prefix path for the structure
    :return: directory structure with keys removed according to the rules
    """
    if prefix is None:
        prefix = os.getcwd()
    for k, v in rules.items():
        if isinstance(v, dict):
            apply_update_rules(v, struct[k], join_path(prefix, k))
        else:
            path = join_path(prefix, k)
            if v == FileOp.NO_OVERWRITE and os.path.exists(path):
                struct.pop(k, None)
            elif v == FileOp.NO_CREATE:
                struct.pop(k, None)
    return struct
