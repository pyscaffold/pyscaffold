"""
Configuration for type checking and `PEP 561`_ support using mypy_.

Please notice other extensions can add mypy plugins of type stub packages
via scaffold options:

- ``typecheck_deps``: Any Python package added to this list will be added to the
  ``deps`` option in the ``typecheck`` task inside ``tox.ini``.
- ``mypy_plugins``: Any `mypy plugin`_ added to this list will be added to the
  ``plugins`` option in the ``[mypy]`` section on ``setup.cfg``

Additionally you can also check if the ``typed`` option exists and is set to ``True``.

Warning:
    This is an **experimental** extension and might be subject to incompatible changes
    (or complete removal) even in minor/patch releases.

.. _PEP 561: https://www.python.org/dev/peps/pep-0561/
.. _mypy: https://mypy.readthedocs.io
.. _mypy plugin: https://mypy.readthedocs.io/en/stable/extending_mypy.html
"""
# TODO: Update docstring and implementation when mypy configuration is migrated to
#       pyproject.toml
from pathlib import Path
from types import SimpleNamespace as Object
from typing import List, Optional

from configupdater import ConfigUpdater, Section

from .. import dependencies as deps
from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure, get_id
from ..log import logger
from ..operations import FileContents
from ..structure import ContentModifier, reify_content
from ..templates import get_template
from . import Extension

TYPECHECK_DEPS: List[str] = []  #: Default list of extra deps (e.g.stubs/mypy plugis)
MYPY_PLUGINS: List[str] = []  #: Default list of mypy plugins to be activated


class Typed(Extension):
    """Add support for type checking as defined in PEP561 via mypy"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """See :func:`pyscaffold.exceptions.Extension.activate`"""
        ids = [get_id(a) for a in actions]

        ref = next((a for a in ids if "namespace_options" in a), "get_default_options")
        actions = self.register(actions, add_opts, after=ref)

        ref = next((a for a in ids if "cirrus:add_files" in a), "define_structure")
        actions = self.register(actions, add_typing_support, after=ref)
        return self.register(actions, update_existing_config, after="version_migration")


# ---- Actions ----


def add_opts(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    opts = opts.copy()
    namespaces = opts.get("ns_list", [""])[-1].split(".")
    opts["typed"] = True
    opts["typecheck_root"] = "/".join(["src", *namespaces])  # needs to be POSIX
    opts["typecheck_deps"] = opts.setdefault("typecheck_deps", []) + TYPECHECK_DEPS
    opts["mypy_plugins"] = opts.setdefault("mypy_plugins", []) + MYPY_PLUGINS
    return struct, opts


def add_typing_support(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    struct = structure.ensure(struct, Path("src", opts["package"], "py.typed"), "")
    struct = structure.modify_contents(struct, ".cirrus.yml", add_typecheck_cirrus)
    struct = structure.modify_contents(struct, "tox.ini", add_typecheck_tox)
    struct = structure.modify_contents(struct, "setup.cfg", add_mypy_setupcfg)
    return struct, opts


def update_existing_config(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    # The changes from `add_typing` will not take effect in the case of updates
    # We need to update existing files in that scenario
    if not opts.get("update"):
        return struct, opts

    modify_file(".cirrus.yml", add_typecheck_cirrus, opts)
    modify_file("tox.ini", add_typecheck_tox, opts)
    modify_file("setup.cfg", add_mypy_setupcfg, opts)
    return struct, opts


# ---- Modifier Functions ----


def add_typecheck_cirrus(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    if not contents:
        return contents

    # Adding a section if not present would require having a YAML parser as dependency
    return contents.replace("TYPE_CHECKING: false", "TYPE_CHECKING: true")


def add_typecheck_tox(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    if not contents:
        return contents

    toxini = ConfigUpdater().read_string(contents or "")
    if "testenv:typecheck" in toxini:
        typecheck = toxini["testenv:typecheck"]
    else:
        typecheck = _section_from_template("tox_ini", "testenv:typecheck", opts)
        toxini.add_section(typecheck)

    deps_list: List[str] = opts.get("typecheck_deps", [])
    dependencies = typecheck.get("deps", Object(value=""))
    dependencies = deps.add(deps.split(dependencies.value), deps_list)
    typecheck.set("deps")
    typecheck["deps"].set_values(dependencies)
    return str(toxini)


def add_mypy_setupcfg(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    """Add [mypy] to setup.cfg"""
    if not contents:
        return contents

    setupcfg = ConfigUpdater().read_string(contents or "")
    if "mypy" in setupcfg:
        mypy = setupcfg["mypy"]
    else:
        # Add before PyScaffold
        mypy = _section_from_template("setup_cfg", "mypy", opts)
        sections = reversed(setupcfg.sections())
        add_after_sect = next(s for s in sections if "pyscaffold" not in s.lower())
        setupcfg[add_after_sect].add_after.section(mypy).space()

    # Plugins
    existing_plugins = mypy.get("plugins", Object(value="")).value
    plugins = [p.strip() for p in existing_plugins.split(",")]
    plugins += opts.get("mypy_plugins", [])
    plugins = list({p: 0 for p in plugins if p}.keys())  # Order-preserv. deduplication
    if plugins:
        mypy["plugins"] = ", ".join(plugins)

    return str(setupcfg)


# ---- Helper Functions ----


def modify_file(
    file: str, modifier: ContentModifier, opts: ScaffoldOpts
) -> Optional[Path]:
    path = opts["project_path"] / file
    if not path.exists():
        return None
    if not opts.get("pretend"):
        updated_content = modifier(path.read_text("utf-8"), opts)
        path.write_text(updated_content, "utf-8")
    logger.report("updated", path)
    return path


def _section_from_template(template: str, section: str, opts: ScaffoldOpts) -> Section:
    doc = ConfigUpdater()
    doc.read_string(reify_content(get_template(template), opts) or "")
    return doc[section].detach()
