"""
Configuration for type checking and `PEP 561`_ support.

Please notice other extensions can integrate with :class:`Typed` by changing the content
of some scaffold options:

- ``typecheck_deps``: Any Python package added to this list will be added to the
  ``deps`` option in the ``typecheck`` task inside ``tox.ini``.
- ``mypy_plugins``: Any `mypy plugin`_ added to this list will be added to the
  ``plugins`` option in the ``[mypy]`` section on ``setup.cfg``

Additionally the ``typed`` option will be set to ``True``.

_PEP 561: https://www.python.org/dev/peps/pep-0561/
_mypy plugin: https://mypy.readthedocs.io/en/stable/extending_mypy.html
"""
# TODO: Update docstring and implementation when mypy configuration is migrated to
#       pyproject.toml
from types import SimpleNamespace as Object
from typing import List, Optional

from configupdater import ConfigUpdater, Section

from .. import dependencies as deps
from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure, get_id
from ..operations import FileContents
from ..structure import ContentModifier, reify_content
from ..templates import get_template

TYPECHECK_DEPS = ["mypy"]
MYPY_PLUGINS: List[str] = []


# ---- Helper Functions ----


def add_typecheck_cirrus(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    if not contents or "typecheck_task:\n" in contents:
        return contents

    new_task = reify_content(get_template("cirrus_typecheck"), opts) or ""
    return "\n\n".join((contents, new_task))


def add_typecheck_tox(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    toxini = ConfigUpdater().read_string(contents or "")
    if not contents or "testenv:typecheck" in toxini:
        return contents

    new_section = _section_from_template("tox_typecheck", "testenv:typecheck", opts)
    toxini.add_section(new_section)
    new_section.add_before.space(2)

    # Ensure typecheck dependencies
    deps_list: List[str] = opts.get("typecheck_deps", [])
    dependencies = new_section.get("deps", Object(value=""))
    dependencies = deps.add(deps.split(dependencies.value), deps_list)
    new_section["deps"].set_values(dependencies)

    return str(toxini)


def add_mypy_config(contents: FileContents, opts: ScaffoldOpts) -> FileContents:
    """Add [mypy] to setup.cfg"""
    setupcfg = ConfigUpdater().read_string(contents or "")

    if not contents or "mypy" in setupcfg:
        return contents

    # Add as last section before PyScaffold
    sections = reversed(setupcfg.sections())
    add_after_sect = next(s for s in sections if "pyscaffold" not in s.lower())
    new_section = _section_from_template("mypy_cfg", "mypy", opts)
    setupcfg[add_after_sect].add_after.section(new_section).space()

    # Plugins
    existing_plugins = new_section.get("plugins", Object(value="")).value
    plugins = [p.strip() for p in existing_plugins.split(",")]
    plugins += opts.get("mypy_plugins", [])
    plugins = list({p: 0 for p in plugins if p}.keys())  # Order-preserv. deduplication
    new_section["plugins"] = ", ".join(plugins)

    return str(setupcfg)


def _section_from_template(template: str, section: str, opts: ScaffoldOpts) -> Section:
    doc = ConfigUpdater()
    doc.read_string(reify_content(get_template(template), opts) or "")
    return doc[section].detach()
