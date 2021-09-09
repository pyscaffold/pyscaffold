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
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
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

TYPECHECK_DEPS = ["mypy"]
MYPY_PLUGINS: List[str] = []
ANNOTATE = ["skeleton"]
"""Names of templates to be annotated

.. important::
   We assume the file produced is ``src/{opts["package"]}/{template}.py`` and that
   a corresponding type stub template exists and is called ``{template}_pyi``.
"""

_TMPFILE_NAME = "_f.py"


class Typed(Extension):
    """Add support for type checking as defined in PEP561"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """See :func:`pyscaffold.exceptions.Extension.activate`"""
        names = (get_id(a) for a in actions)
        ref = next((a for a in names if "cirrus:add_files" in a), "define_structure")
        actions = self.register(actions, add_opts, after="get_default_options")
        actions = self.register(actions, add_typing_support, after=ref)
        actions = self.register(actions, annotate_templates, after="add_typing_support")
        return self.register(actions, update_existing_config, after="version_migration")


# ---- Actions ----


def add_opts(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    opts = opts.copy()
    opts["typed"] = True
    opts["pkg_src"] = Path("src", *opts.get("ns_list", [""])[-1].split("."))
    opts["typecheck_deps"] = opts.setdefault("typecheck_deps", []) + TYPECHECK_DEPS
    opts["mypy_plugins"] = opts.setdefault("mypy_plugins", []) + MYPY_PLUGINS
    return struct, opts


def add_typing_support(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    struct = structure.ensure(struct, Path("src", opts["package"], "py.typed"), "")
    struct = structure.modify_contents(struct, "setup.cfg", add_mypy_config)
    struct = structure.modify_contents(struct, "tox.ini", add_typecheck_tox)
    struct = structure.modify_contents(struct, ".cirrus.yml", add_typecheck_cirrus)
    return struct, opts


def annotate_templates(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    for template in ANNOTATE:
        type_stub = reify_content(get_template(f"{template}_pyi"), opts)
        path = Path("src", opts["package"], template).with_suffix(".py")
        modifier = partial(add_type_annotations, type_stub)
        struct = structure.modify_contents(struct, path, modifier)

    return struct, opts


def update_existing_config(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    # The changes from `add_typing` will not take effect in the case of updates
    # We need to update existing files in that scenario
    if not opts.get("update"):
        return struct, opts

    modify_file("setup.cfg", add_mypy_config, opts)
    modify_file("tox.ini", add_typecheck_tox, opts)
    modify_file(".cirrus.yml", add_typecheck_cirrus, opts)

    return struct, opts


# ---- Helper Functions ----


def modify_file(file: str, modifier: ContentModifier, opts: ScaffoldOpts):
    path = opts["project_path"] / file
    if not opts.get("pretend"):
        updated_content = modifier(path.read_text("utf-8"), opts)
        path.write_text(updated_content, "utf-8")
    logger.report("updated", path)


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


def add_type_annotations(type_stub_contents: str, file_contents: FileContents, _opts):
    if not file_contents or not file_contents.strip():
        return file_contents

    try:
        from retype import retype_file
        from retype.config import ReApplyFlags
    except ImportError as ex:
        raise MissingTypingDependencies() from ex

    with TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        file = tmppath / _TMPFILE_NAME
        file.write_text(file_contents or "", "utf-8")
        file.with_suffix(".pyi").write_text(type_stub_contents, "utf-8")

        flags = ReApplyFlags(replace_any=True, incremental=True)
        out = retype_file(file, tmppath, tmppath, quiet=True, flags=flags)
        typed_content = out.read_text("utf-8")

    return typed_content


def _section_from_template(template: str, section: str, opts: ScaffoldOpts) -> Section:
    doc = ConfigUpdater()
    doc.read_string(reify_content(get_template(template), opts) or "")
    return doc[section].detach()


# ---- Exceptions ----


class MissingTypingDependencies(ImportError):
    """PyScaffold relies on additional packages for the ``--typed`` feature.
    Please install PyScaffold using either ``pip install PyScaffold[typed]``
    or ``pip install PyScaffold[all]``
    """

    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or self.__doc__)
