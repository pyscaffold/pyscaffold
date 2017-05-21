# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""
from __future__ import absolute_import, print_function

import os
from os.path import exists as path_exists
from os.path import join as join_path

from six import string_types

from . import templates, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


class FileOp(object):
    """Namespace for file operations during an update"""

    NO_OVERWRITE = 0
    """Do not overwrite an existing file during update
    (still created if not exists)
    """

    NO_CREATE = 1
    """Do not create the file during an update"""


def add_namespace(opts, struct):
    """Prepend the namespace to a given file structure

    Args:
        opts (dict): options of the project
        struct (dict): directory structure as dictionary of dictionaries

    Returns:
        dict: directory structure as dictionary of dictionaries
    """
    if not opts['namespace']:
        return struct
    namespace = opts['namespace'][-1].split('.')
    base_struct = struct
    pkg_struct = struct[opts['project']][opts['package']]
    struct = base_struct[opts['project']]
    del struct[opts['package']]
    for sub_package in namespace:
        struct[sub_package] = {'__init__.py': templates.namespace(opts)}
        struct = struct[sub_package]
    struct[opts['package']] = pkg_struct
    return base_struct


def make_structure(opts):
    """Creates the project structure as dictionary of dictionaries

    Args:
        opts (dict): options of the project

    Returns:
        dict: structure as dictionary of dictionaries
    """
    struct = {opts['project']: {
        '.gitignore': (templates.gitignore(opts), FileOp.NO_OVERWRITE),
        opts['package']: {'__init__.py': templates.init(opts),
                          'skeleton.py': (templates.skeleton(opts),
                                          FileOp.NO_CREATE)},
        'tests': {'conftest.py': (templates.conftest_py(opts),
                                  FileOp.NO_OVERWRITE),
                  'test_skeleton.py': (templates.test_skeleton(opts),
                                       FileOp.NO_CREATE)},
        'docs': {'conf.py': templates.sphinx_conf(opts),
                 'authors.rst': templates.sphinx_authors(opts),
                 'index.rst': (templates.sphinx_index(opts),
                               FileOp.NO_OVERWRITE),
                 'license.rst': templates.sphinx_license(opts),
                 'changes.rst': templates.sphinx_changes(opts),
                 'Makefile': templates.sphinx_makefile(opts),
                 '_static': {
                     '.gitignore': templates.gitignore_empty(opts)}},
        'README.rst': (templates.readme(opts), FileOp.NO_OVERWRITE),
        'AUTHORS.rst': (templates.authors(opts), FileOp.NO_OVERWRITE),
        'LICENSE.txt': (templates.license(opts), FileOp.NO_OVERWRITE),
        'CHANGES.rst': (templates.changes(opts), FileOp.NO_OVERWRITE),
        'setup.py': templates.setup_py(opts),
        'setup.cfg': (templates.setup_cfg(opts), FileOp.NO_OVERWRITE),
        'requirements.txt': (templates.requirements(opts),
                             FileOp.NO_OVERWRITE),
        'test-requirements.txt': (templates.test_requirements(opts),
                                  FileOp.NO_OVERWRITE),
        '.coveragerc': (templates.coveragerc(opts), FileOp.NO_OVERWRITE)}}
    struct = add_namespace(opts, struct)

    return struct


def create_structure(struct, prefix=None, update=False):
    """Manifests a directory structure in the filesystem

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        prefix (str): prefix path for the structure
        update (bool): update an existing directory structure

    Raises:
        :obj:`RuntimeError`: raised if content type in struct is unknown
    """
    if prefix is None:
        prefix = os.getcwd()
    for name, content in struct.items():
        if isinstance(content, string_types):
            with open(join_path(prefix, name), 'w') as fh:
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
        dict: directory structure with keys removed according to the rules
              (in this tree representation, the leaves are all strings)
    """
    if prefix is None:
        prefix = os.getcwd()

    filtered = {}

    for k, v in struct.items():
        if isinstance(v, dict):
            v = apply_update_rules(v, opts, join_path(prefix, k))
        else:
            path = join_path(prefix, k)
            v = apply_update_rule_to_file(path, v, opts)

        if v:
            filtered[k] = v

    return filtered


def apply_update_rule_to_file(path, value, opts):
    """Returns the content of the file if it should be generated,
    or None otherwise.

    Args:
        path (str): complete file for the path
        value (tuple or str): content (and update rule)
        opts (dict): options of the project, containing the following flags:

            - **update**: when the project already exists and should be updated
            - **force**: overwrite all the files that already exist
    """
    if isinstance(value, (tuple, list)):
        content, rule = value
    else:
        content, rule = value, None

    update = opts.get('update', False)
    force = opts.get('force', False)

    skip = update and not force and (
            rule == FileOp.NO_CREATE or
            path_exists(path) and rule == FileOp.NO_OVERWRITE)

    return None if skip else content
