"""
Collection of functions responsible for the "reification" of the file representation in
the project structure into a file written to the disk. A function that "reifies" a file
is called here a **file operation** or simply a **file op**.

.. versionchanged:: 4.0
   Prior to PyScaffold 4, file operations where simply indicated as a numeric flag
   (the members of ``pyscaffold.structure.FileOp``) in the project structure.
   Starting from PyScaffold 4, file operation are functions with signature given by
   :obj:`FileOp`.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Union

from . import utils
from .log import logger

# Signatures for the documentation purposes

ScaffoldOpts = Dict[str, Any]
"""Dictionary with PyScaffold's options, see :obj:`pyscaffold.api.create_project`.
Should be treated as immutable, if required clone before changing.

Please notice some behaviours given by the options should be observed. For example,
files should be overwritten when the **force** option is ``True``. Similarly when
**pretend** is ``True``, no operation should be really performed, but any action should
be logged as if realized.
"""

FileContents = Union[str, None]
"""When the file content is ``None``, the file should not be written to
disk (empty files are represented by an empty string ``""`` as content).
"""

FileOp = Callable[[Path, "FileContents", "ScaffoldOpts"], Union[Path, None]]
"""Signature of functions considered file operations.
They might write a file to the disk as a side effect.

If the file is written (or more generally changed, such as new access permissions), by
convention they should return the file path. If no file was touched, ``None`` should be
returned.
Please notice a **FileOp** might return ``None`` if a pre-existing file in the disk is
not modified.
"""


# FileOps and FileOp "factories/decorators/wrappers"


def create(path: Path, contents: FileContents, opts: ScaffoldOpts) -> Union[Path, None]:
    """Default :obj:`FileOp`: always create/write the file even during (forced) updates.
    """
    if contents is None:
        return None

    return utils.create_file(path, contents, pretend=opts.get("pretend"))


def no_overwrite(file_op: FileOp = create) -> FileOp:
    """This function is not exactly a :obj:`FileOp`, instead, when called it returns a
    :obj:`FileOp` that do not overwrite an existing file during update (still created if
    not exists). It works similarly to a `decorator`_.

    Args:
        file_op (FileOp): a :obj:`FileOp` that will be "decorated", i.e. will be called
            if the ``no_overwrite`` conditions are met.

    .. decorator: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
    """

    def _no_overwrite(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.file_op.no_overwrite``"""
        if opts.get("force") or not path.exists():
            return file_op(path, contents, opts)

        logger.report("skip", path)
        return None

    return _no_overwrite


def skip_on_update(file_op: FileOp = create) -> FileOp:
    """This function is not exactly a :obj:`FileOp`, instead, when called it returns a
    :obj:`FileOp` that do not create the file during an update.
    It works similarly to a `decorator`_.

    Args:
        file_op (FileOp): a :obj:`FileOp` that will be "decorated", i.e. will be called
            if the ``skip_on_update`` conditions are met.

    .. decorator: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
    """

    def _skip_on_update(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.file_op.skip_on_update``"""
        if opts.get("force") or not opts.get("update"):
            return file_op(path, contents, opts)

        logger.report("skip", path)
        return None

    return _skip_on_update


def with_permissions(permissions: int, file_op: FileOp = create) -> FileOp:
    """This function is not exactly a :obj:`FileOp`, instead, when called it returns a
    :obj:`FileOp` that will **add** permissions to the file (on top of the ones given by
    default by the OS). It works similarly to a `decorator`_.

    Args:
        permissions (int): permissions to be added to file::

                updated file mode = old mode | permissions

            Preferably the values should be a combination of
            :obj`stat.S_* <stat.S_IXUSR>` values (see :obj:`os.chmod`).

        file_op (FileOp): a :obj:`FileOp` that will be "decorated", i.e. if the file
            exists in disk after ``file_op`` is called (either created or pre-existing)
            it will add ``permissions`` to it.

    .. decorator: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
    """

    def _with_permissions(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.file_op.with_permissions``"""
        return_value = file_op(path, contents, opts)

        if path.exists():
            mode = path.stat().st_mode | permissions
            return utils.chmod(path, mode, pretend=opts.get("pretend"))

        return return_value

    return _with_permissions
