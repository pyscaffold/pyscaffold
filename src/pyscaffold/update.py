"""
Functionality to update one PyScaffold version to another
"""
from enum import Enum
from functools import reduce, wraps
from itertools import chain
from types import SimpleNamespace as Object
from typing import TYPE_CHECKING, Callable, Iterable, Tuple

from configupdater import ConfigUpdater
from packaging.version import Version

from . import __version__ as pyscaffold_version
from . import dependencies as deps
from . import templates, toml
from .info import (
    PYPROJECT_TOML,
    SETUP_CFG,
    get_curr_version,
    read_pyproject,
    read_setupcfg,
)
from .log import logger
from .structure import ScaffoldOpts, Structure

if TYPE_CHECKING:  # pragma: no cover
    # ^  avoid circular dependencies in runtime
    from .actions import Action, ActionParams


(ALWAYS,) = list(Enum("VersionUpdate", "ALWAYS"))  # type: ignore
"""Perform the update action regardless of the version"""


def version_migration(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
    """Update projects that were generated with old versions of PyScaffold"""
    update = opts.get("update")

    if not update:
        return struct, opts

    from .actions import invoke  # delay import to avoid circular dependency error

    curr_version = get_curr_version(opts["project_path"])

    # specify how to migrate from one version to another as ordered list
    v4_plan = [
        replace_find_with_find_namespace,  # need to happen after update_setup_cfg
        handover_setup_requires,
        update_pyproject_toml,
    ]
    migration_plans = [
        (Version("3.1"), [add_entrypoints]),
        (ALWAYS, [update_setup_cfg, add_dependencies]),
        (Version("4.0"), v4_plan),
    ]

    plan_actions: Iterable["Action"] = chain.from_iterable(
        plan_actions
        for plan_version, plan_actions in migration_plans
        if plan_version is ALWAYS or curr_version < plan_version
    )

    # replace the old version with the updated one
    opts["version"] = pyscaffold_version
    return reduce(invoke, plan_actions, (struct, opts))


def _change_setupcfg(
    fn: Callable[[ConfigUpdater, ScaffoldOpts], Tuple[ConfigUpdater, ScaffoldOpts]]
) -> Callable[[Structure, ScaffoldOpts], "ActionParams"]:
    @wraps(fn)
    def _wrapped(struct: Structure, opts: ScaffoldOpts) -> "ActionParams":
        setupcfg = read_setupcfg(opts["project_path"])
        setupcfg, opts = fn(setupcfg, opts)
        if not opts["pretend"]:
            try:
                setupcfg.update_file()
            except Exception:  # pragma: no cover
                msg = f"Problems with {fn.__name__}. `setup.cfg` content:\n\n"
                logger.debug(msg + str(setupcfg) + "\n\n")
                raise

        logger.report("updated", opts["project_path"] / SETUP_CFG)
        return struct, opts

    return _wrapped


@_change_setupcfg
def add_entrypoints(setupcfg: ConfigUpdater, opts: ScaffoldOpts):
    """Add [options.entry_points] to setup.cfg"""
    new_section_name = "options.entry_points"
    if new_section_name in setupcfg:
        return setupcfg, opts

    new_section = ConfigUpdater()
    new_section.read_string(templates.setup_cfg(opts))
    new_section = new_section[new_section_name].detach()

    add_after_sect = "options.extras_require"
    if add_after_sect not in setupcfg:
        # user removed it for some reason, default to metadata
        add_after_sect = "metadata"

    setupcfg[add_after_sect].add_after.section(new_section).space()

    return setupcfg, opts


@_change_setupcfg
def update_setup_cfg(setupcfg: ConfigUpdater, opts: ScaffoldOpts):
    """Update `pyscaffold` in setupcfg and ensure some values are there as expected"""
    if "options" not in setupcfg:
        template = templates.setup_cfg(opts)
        new_section = ConfigUpdater().read_string(template)["options"]
        setupcfg["metadata"].add_after.section(new_section.detach())

    # Add "PyScaffold" section if missing and update saved extensions
    setupcfg = templates.add_pyscaffold(setupcfg, opts)
    return setupcfg, opts


@_change_setupcfg
def add_dependencies(setupcfg: ConfigUpdater, opts: ScaffoldOpts):
    """Add dependencies"""
    # TODO: Revise the need for `deps.RUNTIME` once `python_requires = >= 3.8`
    options = setupcfg["options"]
    if "install_requires" in options:
        install_requires = options.get("install_requires", Object(value=""))
        install_requires = deps.add(deps.RUNTIME, deps.split(install_requires.value))
        options["install_requires"].set_values(install_requires)
    else:
        options.set("install_requires")
        options["install_requires"].set_values(deps.RUNTIME)

    return setupcfg, opts


@_change_setupcfg
def replace_find_with_find_namespace(setupcfg: ConfigUpdater, opts: ScaffoldOpts):
    setupcfg["options"].set("packages", "find_namespace:")
    return setupcfg, opts


# Ideally things involving ``no_pyproject`` should be implemented standalone in the
# NoPyProject extension... that is a bit hard though... So we take the pragmatic
# approach => implement things here (do nothing if the user is not using pyproject, but
# migrate the deprecated setup_requires over otherwise)


@_change_setupcfg
def handover_setup_requires(setupcfg: ConfigUpdater, opts: ScaffoldOpts):
    """When paired with :obj:`update_pyproject_toml`, this will transfer ``setup.cfg ::
    options.setup_requires`` to ``pyproject.toml :: build-system.requires``
    """
    options = setupcfg["options"]
    if "setup_requires" in options and opts.get("isolated_build", True):
        setup_requires = options.pop("setup_requires", Object(value=""))
        opts.setdefault("build_deps", []).extend(deps.split(setup_requires.value))

    return setupcfg, opts


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
    toml.setdefault(config, "tool.setuptools_scm.version_scheme", "no-guess-dev")

    (opts["project_path"] / PYPROJECT_TOML).write_text(toml.dumps(config), "utf-8")
    logger.report("updated", opts["project_path"] / PYPROJECT_TOML)
    return struct, opts
