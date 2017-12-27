# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""
from __future__ import absolute_import, print_function

import os
from os.path import exists as path_exists
from os.path import join as join_path

from . import templates, utils
from .contrib.six import string_types
from .log import logger


class FileOp(object):
    """Namespace for file operations during an update"""

    NO_OVERWRITE = 0
    """Do not overwrite an existing file during update
    (still created if not exists)
    """

    NO_CREATE = 1
    """Do not create the file during an update"""


def define_structure(_, opts):
    """Creates the project structure as dictionary of dictionaries

    Args:
        struct (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    struct = {opts['project']: {
        '.gitignore': (templates.gitignore(opts), FileOp.NO_OVERWRITE),
        'src': {
            opts['package']: {'__init__.py': templates.init(opts),
                              'skeleton.py': (templates.skeleton(opts),
                                              FileOp.NO_CREATE)},
        },
        'tests': {'conftest.py': (templates.conftest_py(opts),
                                  FileOp.NO_OVERWRITE),
                  'test_skeleton.py': (templates.test_skeleton(opts),
                                       FileOp.NO_CREATE)},
        'docs': {'conf.py': templates.sphinx_conf(opts),
                 'authors.rst': templates.sphinx_authors(opts),
                 'index.rst': (templates.sphinx_index(opts),
                               FileOp.NO_OVERWRITE),
                 'license.rst': templates.sphinx_license(opts),
                 'changelog.rst': templates.sphinx_changelog(opts),
                 'Makefile': templates.sphinx_makefile(opts),
                 '_static': {
                     '.gitignore': templates.gitignore_empty(opts)}},
        'README.rst': (templates.readme(opts), FileOp.NO_OVERWRITE),
        'AUTHORS.rst': (templates.authors(opts), FileOp.NO_OVERWRITE),
        'LICENSE.txt': (templates.license(opts), FileOp.NO_OVERWRITE),
        'CHANGELOG.rst': (templates.changelog(opts), FileOp.NO_OVERWRITE),
        'setup.py': templates.setup_py(opts),
        'setup.cfg': (templates.setup_cfg(opts), FileOp.NO_OVERWRITE),
        'requirements.txt': (templates.requirements(opts),
                             FileOp.NO_OVERWRITE),
        '.coveragerc': (templates.coveragerc(opts), FileOp.NO_OVERWRITE)}}

    return struct, opts


def create_structure(struct, opts, prefix=None):
    """Manifests a directory structure in the filesystem

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project
        prefix (str): prefix path for the structure

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries (similar to
            input, but only containing the files that actually changed) and
            input options

    Raises:
        :obj:`RuntimeError`: raised if content type in struct is unknown
    """
    update = opts.get('update') or opts.get('force')
    pretend = opts.get('pretend')

    if prefix is None:
        prefix = os.getcwd()

    changed = {}

    for name, content in struct.items():
        if isinstance(content, string_types):
            utils.create_file(join_path(prefix, name), content, pretend)
            changed[name] = content
        elif isinstance(content, dict):
            utils.create_directory(join_path(prefix, name), update, pretend)
            changed[name], _ = create_structure(
                    struct[name], opts, prefix=join_path(prefix, name))
        elif content is None:
            pass
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))

    return changed, opts


def apply_update_rules(struct, opts, prefix=None):
    """Apply update rules using :obj:`~.FileOp` to a directory structure.

    As a result the filtered structure keeps only the files that actually will
    be written.

    Args:
        opts (dict): options of the project, containing the following flags:

            - **update**: when the project already exists and should be updated
            - **force**: overwrite all the files that already exist

        struct (dict): directory structure as dictionary of dictionaries
            (in this tree representation, each leaf can be just a
            string or a tuple also containing an update rule)
        prefix (str): prefix path for the structure

    Returns:
        tuple(dict, dict):
            directory structure with keys removed according to the rules
            (in this tree representation, all the leaves are strings) and input
            options
    """
    if prefix is None:
        prefix = os.getcwd()

    filtered = {}

    for k, v in struct.items():
        if isinstance(v, dict):
            v, _ = apply_update_rules(v, opts, join_path(prefix, k))
        else:
            path = join_path(prefix, k)
            v = apply_update_rule_to_file(path, v, opts)

        if v:
            filtered[k] = v

    return filtered, opts


def apply_update_rule_to_file(path, value, opts):
    """Applies the update rule to a given file path

    Args:
        path (str): file path
        value (tuple or str): content (and update rule)
        opts (dict): options of the project, containing the following flags:

            - **update**: when the project already exists and should be updated
            - **force**: overwrite all the files that already exist

    Returns:
        content of the file if it should be generated or None otherwise.
    """
    if isinstance(value, (tuple, list)):
        content, rule = value
    else:
        content, rule = value, None

    update = opts.get('update')
    force = opts.get('force')

    skip = update and not force and (
            rule == FileOp.NO_CREATE or
            path_exists(path) and rule == FileOp.NO_OVERWRITE)

    if skip:
        logger.report('skip', path)
        return None

    return content
