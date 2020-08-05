"""
Functionality to update one PyScaffold version to another
"""
import os
from enum import Enum
from functools import reduce
from itertools import chain
from pathlib import Path
from pkg_resources import parse_version
from types import SimpleNamespace as Object
from typing import TYPE_CHECKING, Iterable, Union

from configupdater import ConfigUpdater

from . import __version__ as pyscaffold_version
from . import dependencies as deps
from . import templates, toml
from .log import logger
from .structure import ScaffoldOpts, Structure

if TYPE_CHECKING:
    # ^  avoid circular dependencies in runtime
    from .actions import Action, ActionParams

PathLike = Union[str, os.PathLike]

PYPROJECT_TOML: PathLike = "pyproject.toml"
SETUP_CFG: PathLike = "setup.cfg"

ENTRYPOINTS_TEMPLATE = """\
[options.entry_points]
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


def read_setupcfg(path: PathLike, filename=SETUP_CFG) -> ConfigUpdater:
    """Reads-in a configuration file that follows a setup.cfg format.
    Useful for retrieving stored information (e.g. during updates)

    Args:
        path: path where to find the config file
        filename: if ``path`` is a directory, ``name`` will be considered a file
            relative to ``path`` to read (default: setup.cfg)

    Returns:
        Object that can be used to read/edit configuration parameters.
    """
    path = Path(path)
    if path.is_dir():
        path = path / (filename or SETUP_CFG)

    updater = ConfigUpdater()
    updater.read(path, encoding="utf-8")

    logger.report("read", path)

    return updater


def read_pyproject(path: PathLike, filename=PYPROJECT_TOML) -> toml.TOMLMapping:
    """Reads-in a configuration file that follows a pyproject.toml format.

    Args:
        path: path where to find the config file
        filename: if ``path`` is a directory, ``name`` will be considered a file
            relative to ``path`` to read (default: setup.cfg)

    Returns:
        Object that can be used to read/edit configuration parameters.
    """
    file = Path(path)
    if file.is_dir():
        file = file / (filename or PYPROJECT_TOML)

    config = toml.loads(file.read_text(encoding="utf-8"))
    logger.report("read", file)
    return config


def get_curr_version(project_path: PathLike):
    """Retrieves the PyScaffold version that put up the scaffold

    Args:
        project_path: path to project

    Returns:
        Version: version specifier
    """
    setupcfg = read_setupcfg(project_path).to_dict()
    return parse_version(setupcfg["pyscaffold"]["version"])


(ALWAYS,) = list(Enum("VersionUpdate", "ALWAYS"))  # type: ignore


def version_migration(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
    """Update projects that were generated with old versions of PyScaffold"""
    update = opts.get("update")

    if not update:
        return struct, opts

    from .actions import invoke  # delay import to avoid circular dependency error

    curr_version = get_curr_version(opts["project_path"])

    # specify how to migrate from one version to another as ordered list
    migration_plans = [
        (parse_version("3.1"), [add_entrypoints]),
        (ALWAYS, [update_setup_cfg, update_pyproject_toml]),
    ]

    plan_actions: Iterable["Action"] = chain.from_iterable(
        plan_actions
        for plan_version, plan_actions in migration_plans
        if plan_version is ALWAYS or curr_version < plan_version
    )

    # replace the old version with the updated one
    opts["version"] = pyscaffold_version
    return reduce(invoke, plan_actions, (struct, opts))


def add_entrypoints(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
    """Add [options.entry_points] to setup.cfg"""
    setupcfg = read_setupcfg(opts["project_path"])
    new_section_name = "options.entry_points"
    if new_section_name in setupcfg:
        return struct, opts

    new_section = ConfigUpdater()
    new_section.read_string(ENTRYPOINTS_TEMPLATE)
    new_section = new_section[new_section_name]

    add_after_sect = "options.extras_require"
    if add_after_sect not in setupcfg:
        # user removed it for some reason, default to metadata
        add_after_sect = "metadata"

    setupcfg[add_after_sect].add_after.section(new_section).space()

    if not opts["pretend"]:
        setupcfg.update_file()

    return struct, opts


# Ideally things involving ``no_pyproject`` should be implemented standalone in the
# NoPyProject extension... that is a bit hard though... So we take the pragmatic
# approach => implement things here (do nothing if the user is not using pyproject, but
# migrate the deprecated setup_requires over otherwise)


def update_setup_cfg(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
    """Update `pyscaffold` and hand `setup_requires` over to `update_pyproject_toml`"""

    setupcfg = read_setupcfg(opts["project_path"])
    setupcfg["pyscaffold"]["version"] = pyscaffold_version
    options = setupcfg["options"] if "options" in setupcfg else {}

    if "setup_requires" in options and opts.get("isolated_build", True):
        # This will transfer `setup.cfg :: options.setup_requires` to
        # `pyproject.toml :: build-system.requires`
        setup_requires = setupcfg["options"].pop("setup_requires", Object(value=""))
        opts.setdefault("build_deps", []).extend(deps.split(setup_requires.value))

    if not opts["pretend"]:
        setupcfg.update_file()

    return struct, opts


def update_pyproject_toml(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
    """Update old pyproject.toml generated by pyscaffoldext-pyproject and import
    `setup_requires` from `update_setup_cfg` into `build-system.requires`.
    """

    if opts.get("pretend") or not opts.get("isolated_build", True):
        return struct, opts

    try:
        config = read_pyproject(opts["project_path"])
    except FileNotFoundError:
        # We still need to transfer ``setup_requires`` to pyproject.toml
        config = toml.loads(templates.pyproject_toml(opts))

    build = config["build-system"]
    existing = deps.add(opts.get("build_deps", []), build.get("requires", []))
    build["requires"] = deps.remove(deps.add(existing, deps.ISOLATED), ["pyscaffold"])
    # ^  PyScaffold is no longer a build dependency
    toml.setdefault(build, "build-backend", "setuptools.build_meta")
    toml.setdefault(config, "tool.setuptools_scm.version_scheme", "post-release")

    (opts["project_path"] / PYPROJECT_TOML).write_text(toml.dumps(config), "utf-8")
    return struct, opts
