# -*- coding: utf-8 -*-
"""
Functionality to update one PyScaffold version to another
"""
import os
from functools import reduce
from os.path import exists as path_exists
from os.path import join as join_path

from pkg_resources import parse_version

from . import __version__ as pyscaffold_version
from .contrib.configupdater import ConfigUpdater
from .log import logger
from .structure import FileOp
from .utils import get_id, get_setup_requires_version


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

        if v is not None:
            filtered[k] = v

    return filtered, opts


def apply_update_rule_to_file(path, value, opts):
    """Applies the update rule to a given file path

    Args:
        path (str): file path
        value (tuple or str): content (and update rule)
        opts (dict): options of the project, containing the following flags:

            - **update**: if the project already exists and should be updated
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


def read_setupcfg(project_path):
    """Reads-in setup.cfg for updating

    Args:
        project_path (str): path to project

    Returns:

    """
    path = join_path(project_path, 'setup.cfg')
    updater = ConfigUpdater()
    updater.read(path, encoding='utf-8')
    return updater


def invoke_action(action, struct, opts):
    """Invoke action with proper logging.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`.
        opts (dict): given options, see :obj:`create_project` for
            an extensive list.

    Returns:
        tuple(dict, dict): updated project representation and options
    """
    logger.report('invoke', get_id(action))
    with logger.indent():
        struct, opts = action(struct, opts)

    return struct, opts


def get_curr_version(project_path):
    """Retrieves the PyScaffold version that put up the scaffold

    Args:
        project_path: path to project

    Returns:
        Version: version specifier
    """
    setupcfg = read_setupcfg(project_path).to_dict()
    return parse_version(setupcfg['pyscaffold']['version'])


def version_migration(struct, opts):
    """Migrations from one version to another

    Args:
        struct (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    update = opts.get('update')

    if not update:
        return struct, opts

    curr_version = get_curr_version(opts['project'])

    # specify how to migrate from one version to another as ordered list
    migration_plans = [
        (parse_version('3.1'), [add_entrypoints,
                                add_setup_requires])
    ]
    for plan_version, plan_actions in migration_plans:
        if curr_version < plan_version:
            struct, opts = reduce(lambda acc, f: invoke_action(f, *acc),
                                  plan_actions, (struct, opts))

    # note the updating version in setup.cfg for future use
    update_pyscaffold_version(opts['project'], opts['pretend'])
    # replace the old version with the updated one
    opts['version'] = pyscaffold_version
    return struct, opts


def add_entrypoints(struct, opts):
    """Add [options.entry_points] to setup.cfg

    Args:
        struct (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    setupcfg = read_setupcfg(opts['project'])
    section_str = """[options.entry_points]
# Add here console scripts like:
# console_scripts =
#     script_name = ${package}.module:function
# For example:
# console_scripts =
#     fibonacci = ${package}.skeleton:run
# And any other entry points, for example:
# pyscaffold.cli =
#     awesome = pyscaffoldext.awesome.extension:AwesomeExtension
    """
    new_section_name = 'options.entry_points'
    if new_section_name in setupcfg:
        return struct, opts

    new_section = ConfigUpdater()
    new_section.read_string(section_str)
    new_section = new_section[new_section_name]

    add_after_sect = 'options.extras_require'
    if add_after_sect not in setupcfg:
        # user removed it for some reason, default to metadata
        add_after_sect = 'metadata'

    setupcfg[add_after_sect].add_after.section(new_section).space()
    if not opts['pretend']:
        setupcfg.update_file()
    return struct, opts


def add_setup_requires(struct, opts):
    """Add `setup_requires` in setup.cfg

    Args:
        struct (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    setupcfg = read_setupcfg(opts['project'])
    comment = ("# DON'T CHANGE THE FOLLOWING LINE! "
               "IT WILL BE UPDATED BY PYSCAFFOLD!")
    options = setupcfg['options']
    if 'setup_requires' in options:
        return struct, opts

    version_str = get_setup_requires_version()
    (options['package_dir'].add_after
                           .comment(comment)
                           .option('setup_requires', version_str))
    if not opts['pretend']:
        setupcfg.update_file()
    return struct, opts


def update_pyscaffold_version(project_path, pretend):
    """Update `setup_requires` in setup.cfg

    Args:
        project_path (str): path to project
        pretend (bool): only pretend to do something
    """
    setupcfg = read_setupcfg(project_path)
    setupcfg['options']['setup_requires'] = get_setup_requires_version()
    setupcfg['pyscaffold']['version'] = pyscaffold_version
    if not pretend:
        setupcfg.update_file()
