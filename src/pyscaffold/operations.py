"""
Collection of functions responsible for the "reification" of the file representation in
the project structure into a file written to the disk.

A function that "reifies" a file (manifests the programmatic representation of the file
in the project structure dictionary to the disk) is called here a **file operation** or
simply a **file op**. Actually file ops don't even need to be functions strictly
speaking, they can be any :obj:`callable` object. The only restriction is that file ops
**MUST** respect the :obj:`FileOp` signature. The :obj:`create` function is a good
example of how to write a new file op.

A function (or callable) that modifies the behaviour of an existing file op, by wrapping
it with another function/callable is called here **modifier**. Modifiers work similarly
to Python `decorators`_ and allow extending/refining the existing file ops.
A modifier should receive a file op as argument and return another file op.
:obj:`no_overwrite` and :obj:`skip_on_update` are good examples on how to write new file
op modifiers.

While modifiers don't have a specific signature (the number of parameters might vary,
but they always return a single file op value), the following conventions **SHOULD** be
observed when creating new modifiers:

- Modifiers should accept at least one argument: the **file op** they modify
  (you don't have to be very creative, go ahead and name this parameter ``file_op``, it
  is a good convention).
  This parameter should be made **optional** (the default value of :obj:`create` usually
  works, unless there is a better default value for the main use case of the modifier).
- Modifiers can accept arguments other then the file op they modify. These arguments
  should **precede** the file op in the list of arguments (the file op should be the
  last argument, which interoperates well with :obj:`~functools.partial`).
- When writing a modifier that happens to be a function (instead of a callable class),
  please name the inner function with the same name of the modifier but preceded by an
  ``_`` (underscore) char. This allows better inspection/debugging.


.. versionchanged:: 4.0
   Previously, file operations where simply indicated as a numeric flag
   (the members of ``pyscaffold.structure.FileOp``) in the project structure.
   Starting from PyScaffold 4, file operation are functions with signature given by
   :obj:`FileOp`.

.. _decorators: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
.. _shebang: https://en.wikipedia.org/wiki/Shebang_(Unix)
.. _File access permissions: https://en.wikipedia.org/wiki/File_system_permissions
"""

from pathlib import Path
from typing import Any, Callable, Dict, Union

from . import file_system as fs
from .log import logger

# Signatures for the documentation purposes

ScaffoldOpts = Dict[str, Any]
"""Dictionary with PyScaffold's options, see :obj:`pyscaffold.api.create_project`.
Should be treated as immutable (if required, copy before changing).

Please notice some behaviours given by the options **SHOULD** be observed. For example,
files should be overwritten when the **force** option is ``True``. Similarly when
**pretend** is ``True``, no operation should be really performed, but any action should
be logged as if realized.
"""

FileContents = Union[str, None]
"""When the file content is ``None``, the file should not be written to
disk (empty files are represented by an empty string ``""`` as content).
"""

FileOp = Callable[[Path, FileContents, ScaffoldOpts], Union[Path, None]]
"""Signature of functions considered file operations::

    Callable[[Path, FileContents, ScaffoldOpts], Union[Path, None]]

Args:
    path (pathlib.Path): file path potentially to be written to/changed in the disk.
    contents (:obj:`FileContents`): usually a string that represents a text
        content of the file. :obj:`None` indicates the file should not be written.
    opts (:obj:`ScaffoldOpts`): a dict with PyScaffold's options.

Returns:
    If the file is written (or more generally changed, such as new access permissions),
    by convention they should return the :obj:`file path <pathlib.Path>`.
    If no file was touched, :obj:`None` should be returned. Please notice a **FileOp**
    might return :obj:`None` if a pre-existing file in the disk is not modified.

Note:
    A **FileOp** usually has side effects (e.g. write a file to the disk), see
    :obj:`FileFileContents` and :obj:`ScaffoldOpts` for other conventions.
"""


# FileOps and FileOp modifiers (a.k.a. factories/decorators/wrappers)


def create(path: Path, contents: FileContents, opts: ScaffoldOpts) -> Union[Path, None]:
    """
    Default :obj:`FileOp`: always create/write the file even during (forced) updates.
    """
    if contents is None:
        return None

    return fs.create_file(path, contents, pretend=opts.get("pretend"))


def remove(path: Path, _content: FileContents, opts: ScaffoldOpts) -> Union[Path, None]:
    """Remove the file if it exists in the disk"""
    if not path.exists():
        return None

    return fs.rm_rf(path, pretend=opts.get("pretend"))


def no_overwrite(file_op: FileOp = create) -> FileOp:
    """File op modifier. Returns a :obj:`FileOp` that does not overwrite an existing
    file during update (still created if not exists).

    Args:
        file_op: a :obj:`FileOp` that will be "decorated",
            i.e. will be called if the ``no_overwrite`` conditions are met.
            Default: :obj:`create`.
    """

    def _no_overwrite(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.operations.no_overwrite``"""
        if opts.get("force") or not path.exists():
            return file_op(path, contents, opts)

        logger.report("skip", path)
        return None

    return _no_overwrite


def skip_on_update(file_op: FileOp = create) -> FileOp:
    """File op modifier. Returns a :obj:`FileOp` that will skip the file during a
    project update (the file will just be created for brand new projects).

    Args:
        file_op: a :obj:`FileOp` that will be "decorated",
            i.e. will be called if the ``skip_on_update`` conditions are met.
            Default: :obj:`create`.
    """

    def _skip_on_update(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.operations.skip_on_update``"""
        if opts.get("force") or not opts.get("update"):
            return file_op(path, contents, opts)

        logger.report("skip", path)
        return None

    return _skip_on_update


def add_permissions(permissions: int, file_op: FileOp = create) -> FileOp:
    """File op modifier. Returns a :obj:`FileOp` that will **add** access permissions to
    the file (on top of the ones given by default by the OS).

    Args:
        permissions (int): permissions to be added to file::

                updated file mode = old mode | permissions  (bitwise OR)

            Preferably the values should be a combination of
            :obj:`stat.S_* <stat.S_IRUSR>` values (see :obj:`os.chmod`).

        file_op: a :obj:`FileOp` that will be "decorated".
            If the file exists in disk after ``file_op`` is called (either created
            or pre-existing), ``permissions`` will be added to it.
            Default: :obj:`create`.

    Warning:
        This is an **experimental** file op and might be subject to incompatible changes
        (or complete removal) even in minor/patch releases.

    Note:
        `File access permissions`_ work in a completely different way depending on the
        operating system. This file op is straightforward on POSIX systems, but a bit
        tricky on Windows. It should be safe for desirable but not required effects
        (e.g. making a file with a `shebang`_ executable, but that can also run via
        ``python FILE``), or ensuring files are readable/writable.
    """

    def _add_permissions(path: Path, contents: FileContents, opts: ScaffoldOpts):
        """See ``pyscaffold.operations.add_permissions``"""
        return_value = file_op(path, contents, opts)

        if path.exists():
            mode = path.stat().st_mode | permissions
            return fs.chmod(path, mode, pretend=opts.get("pretend"))

        return return_value

    return _add_permissions
