# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""

from functools import singledispatch
from pathlib import Path
from typing import Tuple, Union

from . import templates, utils
from .file_op import FileContents, FileOp, create, no_overwrite, skip_on_update

StructureLeaf = Tuple[FileContents, FileOp]

NO_OVERWRITE = no_overwrite()
SKIP_ON_UPDATE = skip_on_update()


def define_structure(_, opts):
    """Creates the project structure as dictionary of dictionaries

    Args:
        _ (dict): previous directory structure (ignored)
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            structure as dictionary of dictionaries and input options
    """
    struct = {
        ".gitignore": (templates.gitignore(opts), NO_OVERWRITE),
        "src": {
            opts["package"]: {
                "__init__.py": templates.init(opts),
                "skeleton.py": (templates.skeleton(opts), SKIP_ON_UPDATE),
            }
        },
        "tests": {
            "conftest.py": (templates.conftest_py(opts), NO_OVERWRITE),
            "test_skeleton.py": (templates.test_skeleton(opts), SKIP_ON_UPDATE),
        },
        "docs": {
            "conf.py": templates.sphinx_conf(opts),
            "authors.rst": templates.sphinx_authors(opts),
            "index.rst": (templates.sphinx_index(opts), NO_OVERWRITE),
            "license.rst": templates.sphinx_license(opts),
            "changelog.rst": templates.sphinx_changelog(opts),
            "Makefile": templates.sphinx_makefile(opts),
            "_static": {".gitignore": templates.gitignore_empty(opts)},
        },
        "README.rst": (templates.readme(opts), NO_OVERWRITE),
        "AUTHORS.rst": (templates.authors(opts), NO_OVERWRITE),
        "LICENSE.txt": (templates.license(opts), NO_OVERWRITE),
        "CHANGELOG.rst": (templates.changelog(opts), NO_OVERWRITE),
        "setup.py": templates.setup_py(opts),
        "setup.cfg": (templates.setup_cfg(opts), NO_OVERWRITE),
        ".coveragerc": (templates.coveragerc(opts), NO_OVERWRITE),
    }

    return struct, opts


@singledispatch
def structure_leaf(contents: Union[None, str, StructureLeaf]) -> StructureLeaf:
    """Normalize project structure leaf to be a Tuple[FileContents, FileOp]"""
    raise RuntimeError(
        "Don't know what to do with content type " "{type}.".format(type=type(contents))
    )


@structure_leaf.register(str)
@structure_leaf.register(type(None))
# ^  getting types automatically via annotations is not supported before 3.7
def _file_contents(contents: FileContents):
    return (contents, create)


@structure_leaf.register(tuple)
def _structure_leaf(contents: StructureLeaf) -> StructureLeaf:
    return (contents[0], contents[1])


def create_structure(struct, opts, prefix=None):
    """Manifests/reifies a directory structure in the filesystem

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project
        prefix (pathlib.PurePath): prefix path for the structure

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries (similar to
            input, but only containing the files that actually changed) and
            input options

    Raises:
        :obj:`RuntimeError`: raised if content type in struct is unknown
    """
    update = opts.get("update") or opts.get("force")
    pretend = opts.get("pretend")

    if prefix is None:
        prefix = opts.get("project_path", ".")
        utils.create_directory(prefix, update, pretend)
    prefix = Path(prefix)

    changed = {}

    for name, content in struct.items():
        if isinstance(content, dict):
            utils.create_directory(prefix / name, update, pretend)
            changed[name], _ = create_structure(
                struct[name], opts, prefix=prefix / name
            )
        else:
            content, file_op = structure_leaf(content)
            if file_op(prefix / name, content, opts):
                changed[name] = content

    return changed, opts
