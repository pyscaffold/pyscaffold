# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""
from __future__ import absolute_import, print_function

import os
from os.path import join as join_path

from six import string_types

from . import shell, templates, utils

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


def add_namespace(opts, struct):
    """
    Prepend the namespace to a given file structure

    :param opts: options as dictionary
    :param struct: directory structure as dictionary of dictionaries
    :return: directory structure as dictionary of dictionaries
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
    """
    Creates the project structure as dictionary of dictionaries

    :param opts: options as dictionary
    :return: structure as dictionary of dictionaries
    """
    struct = {opts['project']: {
        '.gitignore': templates.gitignore(opts),
        opts['package']: {'__init__.py': templates.init(opts),
                          'skeleton.py': templates.skeleton(opts)},
        'tests': {'conftest.py': templates.conftest_py(opts),
                  'test_skeleton.py': templates.test_skeleton(opts)},
        'docs': {'conf.py': templates.sphinx_conf(opts),
                 'authors.rst': templates.sphinx_authors(opts),
                 'index.rst': templates.sphinx_index(opts),
                 'license.rst': templates.sphinx_license(opts),
                 'changes.rst': templates.sphinx_changes(opts),
                 'Makefile': templates.sphinx_makefile(opts),
                 '_static': {
                     '.gitignore': templates.gitignore_empty(opts)}},
        'README.rst': templates.readme(opts),
        'AUTHORS.rst': templates.authors(opts),
        'LICENSE.txt': templates.license(opts),
        'CHANGES.rst': templates.changes(opts),
        'setup.py': templates.setup_py(opts),
        'setup.cfg': templates.setup_cfg(opts),
        'requirements.txt': templates.requirements(opts),
        'test-requirements.txt': templates.test_requirements(opts),
        '.coveragerc': templates.coveragerc(opts)}}
    proj_dir = struct[opts['project']]
    if opts['travis']:
        proj_dir['.travis.yml'] = templates.travis(opts)
        proj_dir['tests']['travis_install.sh'] = templates.travis_install(opts)
    if opts['pre_commit']:
        proj_dir['.pre-commit-config.yaml'] = templates.pre_commit_config(opts)
    if opts['tox']:
        proj_dir['tox.ini'] = templates.tox(opts)
    if opts['update'] and not opts['force']:
        # Do not overwrite following files
        rules = {opts['project']: {
            '.gitignore': FileOp.NO_OVERWRITE,
            '.gitattributes': FileOp.NO_OVERWRITE,
            'setup.cfg': FileOp.NO_OVERWRITE,
            'README.rst': FileOp.NO_OVERWRITE,
            'CHANGES.rst': FileOp.NO_OVERWRITE,
            'LICENSE.txt': FileOp.NO_OVERWRITE,
            'AUTHORS.rst': FileOp.NO_OVERWRITE,
            'requirements.txt': FileOp.NO_OVERWRITE,
            '.travis.yml': FileOp.NO_OVERWRITE,
            '.coveragerc': FileOp.NO_OVERWRITE,
            '.pre-commit-config.yaml': FileOp.NO_OVERWRITE,
            'tox.ini': FileOp.NO_OVERWRITE,
            opts['package']: {'skeleton.py': FileOp.NO_CREATE},
            'tests': {'conftest.py': FileOp.NO_OVERWRITE,
                      'travis_install.sh': FileOp.NO_OVERWRITE,
                      'test_skeleton.py': FileOp.NO_CREATE},
            'docs': {'index.rst': FileOp.NO_OVERWRITE}
        }}
        struct = apply_update_rules(rules, struct)
    struct = add_namespace(opts, struct)

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


def create_django_proj(opts):
    """
    Creates a standard Django project with django-admin.py

    :param opts: options as dictionary
    """
    try:
        shell.django_admin('--version')
    except:
        raise RuntimeError("django-admin.py is not installed, "
                           "run: pip install django")
    shell.django_admin('startproject', opts['project'])


def create_cookiecutter(opts):
    """
    Create a cookie cutter template

    :param opts: options as dictionary
    """
    try:
        from cookiecutter.main import cookiecutter
    except:
        raise RuntimeError("cookiecutter is not installed, "
                           "run: pip install cookiecutter")
    extra_context = dict(full_name=opts['author'],
                         email=opts['email'],
                         project_name=opts['project'],
                         repo_name=opts['package'],
                         project_short_description=opts['description'],
                         release_date=opts['release_date'],
                         version='unknown',  # will be replaced later
                         year=opts['year'])

    cookiecutter(opts['cookiecutter_template'],
                 no_input=True,
                 extra_context=extra_context)


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
