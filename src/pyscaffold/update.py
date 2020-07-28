"""
Functionality to update one PyScaffold version to another
"""
from functools import reduce
from pathlib import Path

from pkg_resources import parse_version

from configupdater import ConfigUpdater

from . import __version__ as pyscaffold_version
from . import dependencies as deps
from .log import logger


def read_setupcfg(path, filename=None):
    """Reads-in a configuration file that follows a setup.cfg format.
    Useful for retrieving stored information (e.g. during updates)

    Args:
        path (os.PathLike): path where to find the config file
        filename (os.PathLike): if ``path`` is a directory,
            ``name`` will be considered a file relative to ``path``
            to read (default: setup.cfg)

    Returns:
        ConfigUpdater: object that can be used to read/edit configuration
            parameters.
    """
    path = Path(path)
    if path.is_dir():
        path = path / (filename or "setup.cfg")

    updater = ConfigUpdater()
    updater.read(path, encoding="utf-8")

    logger.report("read", path)

    return updater


def get_curr_version(project_path):
    """Retrieves the PyScaffold version that put up the scaffold

    Args:
        project_path: path to project

    Returns:
        Version: version specifier
    """
    setupcfg = read_setupcfg(project_path).to_dict()
    return parse_version(setupcfg["pyscaffold"]["version"])


def version_migration(struct, opts):
    """Migrations from one version to another

    Args:
        struct (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    update = opts.get("update")

    if not update:
        return struct, opts

    from .actions import invoke  # delay import to avoid circular dependency error

    curr_version = get_curr_version(opts["project_path"])

    # specify how to migrate from one version to another as ordered list
    migration_plans = [(parse_version("3.1"), [add_entrypoints, add_setup_requires])]
    for plan_version, plan_actions in migration_plans:
        if curr_version < plan_version:
            struct, opts = reduce(invoke, plan_actions, (struct, opts))

    # note the updating version in setup.cfg for future use
    update_pyscaffold_version(opts["project_path"], opts["pretend"])
    # replace the old version with the updated one
    opts["version"] = pyscaffold_version
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
    setupcfg = read_setupcfg(opts["project_path"])
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
    new_section_name = "options.entry_points"
    if new_section_name in setupcfg:
        return struct, opts

    new_section = ConfigUpdater()
    new_section.read_string(section_str)
    new_section = new_section[new_section_name]

    add_after_sect = "options.extras_require"
    if add_after_sect not in setupcfg:
        # user removed it for some reason, default to metadata
        add_after_sect = "metadata"

    setupcfg[add_after_sect].add_after.section(new_section).space()
    if not opts["pretend"]:
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
    setupcfg = read_setupcfg(opts["project_path"])
    comment = "# AVOID CHANGING SETUP_REQUIRES! IT WILL BE UPDATED BY PYSCAFFOLD!"
    options = setupcfg["options"]
    if "setup_requires" in options:
        return struct, opts

    build_deps_str = deps.get_requirements_str()
    (
        options["package_dir"]
        .add_after.comment(comment)
        .option("setup_requires", build_deps_str)
    )
    if not opts["pretend"]:
        setupcfg.update_file()
    return struct, opts


def update_pyscaffold_version(project_path, pretend):
    """Update `setup_requires` in setup.cfg

    Args:
        project_path (str): path to project
        pretend (bool): only pretend to do something
    """
    setupcfg = read_setupcfg(project_path)
    setup_requires = setupcfg["options"].get("setup_requires")
    existing = deps.split(setup_requires.value if setup_requires else "")
    # Remove PyScaffold since it is no longer a build-time dependency
    existing = deps.remove(existing, ["pyscaffold"])
    setupcfg["options"]["setup_requires"] = deps.get_requirements_str(existing)
    setupcfg["pyscaffold"]["version"] = pyscaffold_version
    if not pretend:
        setupcfg.update_file()
