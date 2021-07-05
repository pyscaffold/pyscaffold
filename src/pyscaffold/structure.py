"""Functionality to generate and work with the directory structure of a project.

.. versionchanged:: 4.0
   ``Callable[[dict], str]`` and :obj:`string.Template` objects can also be used as file
   contents. They will be called with PyScaffold's ``opts`` (:obj:`string.Template` via
   :obj:`~string.Template.safe_substitute`)
"""
from copy import deepcopy
from pathlib import Path
from string import Template
from typing import Callable, Dict, Optional, Tuple, Union, cast

from . import templates
from .file_system import PathLike, create_directory
from .operations import (
    FileContents,
    FileOp,
    ScaffoldOpts,
    create,
    no_overwrite,
    skip_on_update,
)
from .templates import get_template

NO_OVERWRITE = no_overwrite()
SKIP_ON_UPDATE = skip_on_update()


# Sphinx is bad at documenting aliases for the time being... so we repeat the definition

AbstractContent = Union[FileContents, Callable[[ScaffoldOpts], FileContents], Template]
"""*Recipe* for obtaining file contents
::

    Union[FileContents, Callable[[ScaffoldOpts], FileContents], Template]
"""

ResolvedLeaf = Tuple[AbstractContent, FileOp]
"""Complete *recipe* for manipulating a file in disk (not only its contents but also the
file operation::

    Tuple[AbstractContent, FileOp]
"""

ReifiedLeaf = Tuple[FileContents, FileOp]
"""Similar to :obj:`ResolvedLeaf` but with file contents "reified", i.e. an actual
string instead of a "lazy object" (such as a function or template).
"""

Leaf = Union[AbstractContent, ResolvedLeaf]
"""Just the content of the file OR a tuple of content + file operation
::

    Union[AbstractContent, ResolvedLeaf]
"""

# TODO: Replace `dict` when recursive types are processed by mypy
Node = Union[Leaf, dict]
"""Representation of a *file system node* in the project structure (e.g. files,
directories::

    Union[Leaf, Structure]
"""


Structure = Dict[str, Node]
"""The directory tree represented as a (possibly nested) dictionary::

    Structure = Dict[str, Node]
    Node = Union[Leaf, Structure]

The keys indicate the path where a file will be written, while the
value indicates the content.

A nested dictionary represent a nested directory, while :obj:`str`,
:obj:`string.Template` and :obj:`callable` values represent a file to be created.
:obj:`tuple` values are also allowed, and in that case, the first element of the tuple
represents the file content while the second element is a :mod:`pyscaffold.operations
<file operation>` (which can be seen as a recipe on how to create a file with the given
content). :obj:`Callable <callable>` file contents are transformed into strings by
calling them with :obj:`PyScaffold's option dict as argument
<pyscaffold.api.create_structure>`. Similarly, :obj:`string.Template.safe_substitute`
are called with PyScaffold's opts.

The top level keys in the dict are file/dir names relative to the project root, while
keys in nested dicts are relative to the parent's key/location.

For example::

    from pyscaffold.operations import no_overwrite
    struct: Structure = {
        'namespace': {
            'module.py': ('print("Hello World!")', no_overwrite())
        }
    }

represents a ``namespace/module.py`` file inside the project folder
with content ``print("Hello World!")``, that will be created only if not
present.

Note:
    :obj:`None` file contents are ignored and not created in disk.
"""

ActionParams = Tuple[Structure, ScaffoldOpts]
"""See :obj:`pyscaffold.actions.ActionParams`"""


# -------- PyScaffold Actions --------


def define_structure(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Creates the project structure as dictionary of dictionaries

    Args:
        struct : previous directory structure (usually and empty dict)
        opts: options of the project

    Returns:
        Project structure and PyScaffold's options

    .. versionchanged:: 4.0
       :obj:`string.Template` and functions added directly to the file structure.
    """
    files: Structure = {
        # Tools
        ".gitignore": (get_template("gitignore"), NO_OVERWRITE),
        ".coveragerc": (get_template("coveragerc"), NO_OVERWRITE),
        ".readthedocs.yml": (get_template("rtd_cfg"), NO_OVERWRITE),
        # Project configuration
        "pyproject.toml": (templates.pyproject_toml, NO_OVERWRITE),
        "setup.py": get_template("setup_py"),
        "setup.cfg": (templates.setup_cfg, NO_OVERWRITE),
        "tox.ini": (get_template("tox_ini"), NO_OVERWRITE),
        # Essential docs
        "README.rst": (get_template("readme"), NO_OVERWRITE),
        "AUTHORS.rst": (get_template("authors"), NO_OVERWRITE),
        "LICENSE.txt": (templates.license, NO_OVERWRITE),
        "CHANGELOG.rst": (get_template("changelog"), NO_OVERWRITE),
        "CONTRIBUTING.rst": (get_template("contributing"), NO_OVERWRITE),
        # Code
        "src": {
            opts["package"]: {
                "__init__.py": templates.init,
                "skeleton.py": (get_template("skeleton"), SKIP_ON_UPDATE),
            }
        },
        # Tests
        "tests": {
            "conftest.py": (get_template("conftest_py"), NO_OVERWRITE),
            "test_skeleton.py": (get_template("test_skeleton"), SKIP_ON_UPDATE),
        },
        # Remaining of the Documentation
        "docs": {
            "conf.py": get_template("sphinx_conf"),
            "authors.rst": get_template("sphinx_authors"),
            "contributing.rst": get_template("sphinx_contributing"),
            "index.rst": (get_template("sphinx_index"), NO_OVERWRITE),
            "readme.rst": get_template("sphinx_readme"),
            "license.rst": get_template("sphinx_license"),
            "changelog.rst": get_template("sphinx_changelog"),
            "Makefile": get_template("sphinx_makefile"),
            "_static": {".gitignore": get_template("gitignore_empty")},
            "requirements.txt": (get_template("rtd_requirements"), NO_OVERWRITE),
        },
    }

    return merge(struct, files), opts


def create_structure(
    struct: Structure, opts: ScaffoldOpts, prefix: Optional[Path] = None
) -> ActionParams:
    """Manifests/reifies a directory structure in the filesystem

    Args:
        struct: directory structure as dictionary of dictionaries
        opts: options of the project
        prefix: prefix path for the structure

    Returns:
        Directory structure as dictionary of dictionaries (similar to input, but only
        containing the files that actually changed) and input options

    Raises:
        TypeError: raised if content type in struct is unknown

    .. versionchanged:: 4.0
       Also accepts :obj:`string.Template` and :obj:`callable` objects as file contents.
    """
    update = opts.get("update") or opts.get("force")
    pretend = opts.get("pretend")

    if prefix is None:
        prefix = cast(Path, opts.get("project_path", "."))
        create_directory(prefix, update, pretend)
    prefix = Path(prefix)

    changed: Structure = {}

    for name, node in struct.items():
        path = prefix / name
        if isinstance(node, dict):
            create_directory(path, update, pretend)
            changed[name], _ = create_structure(node, opts, prefix=path)
        else:
            content, file_op = reify_leaf(node, opts)
            if file_op(path, content, opts):
                changed[name] = content

    return changed, opts


# -------- Auxiliary Functions --------


def resolve_leaf(contents: Leaf) -> ResolvedLeaf:
    """Normalize project structure leaf to be a Tuple[AbstractContent, FileOp]"""
    if isinstance(contents, tuple):
        return contents
    return (contents, create)


def reify_content(content: AbstractContent, opts: ScaffoldOpts) -> FileContents:
    """Make content string (via __call__ or safe_substitute with opts if necessary)"""
    if callable(content):
        return content(opts)
    if isinstance(content, Template):
        return content.safe_substitute(opts)
    return content


def reify_leaf(contents: Leaf, opts: ScaffoldOpts) -> ReifiedLeaf:
    """Similar to :obj:`resolve_leaf` but applies :obj:`reify_content` to the first
    element of the returned tuple.
    """
    file_contents, action = resolve_leaf(contents)
    return (reify_content(file_contents, opts), action)


# -------- Structure Manipulation --------


def modify(
    struct: Structure,
    path: PathLike,
    modifier: Callable[[AbstractContent, FileOp], ResolvedLeaf],
) -> Structure:
    """Modify the contents of a file in the representation of the project tree.

    If the given path does not exist, the parent directories are automatically
    created.

    Args:
        struct: project representation as (possibly) nested dict. See :obj:`~.merge`.

        path: path-like string or object relative to the structure root.
            The following examples are equivalent::

                from pathlib import Path

                'docs/api/index.html'
                Path('docs', 'api', 'index.html')

            .. versionchanged:: 4.0
               The function no longer accepts a list of strings of path parts.

        modifier: function (or callable object) that receives the
            old content and the old file operation as arguments and returns
            a tuple with the new content and new file operation.
            Note that, if the file does not exist in ``struct``, ``None`` will
            be passed as argument. Example::

                modifier = lambda old, op: ((old or '') + 'APPENDED CONTENT'!, op)
                modifier = lambda old, op: ('PREPENDED CONTENT!' + (old or ''), op)

            .. versionchanged:: 4.0
               ``modifier`` requires 2 arguments and now is a mandatory argument.

    .. versionchanged:: 4.0
       ``update_rule`` is no longer an argument. Instead the arity ``modifier`` was
       changed to accept 2 arguments instead of only 1. This is more suitable to
       handling the new :obj:`pyscaffold.operations` API.

    Returns:
        Updated project tree representation

    Note:
        Use an empty string as content to ensure a file is created empty
        (``None`` contents will not be created).
    """
    # Retrieve a list of parts from a path-like object
    path_parts = Path(path).parts

    # Walk the entire path, creating parents if necessary.
    root = deepcopy(struct)
    last_parent: dict = root
    name = path_parts[-1]
    for parent in path_parts[:-1]:
        last_parent = last_parent.setdefault(parent, {})

    # Get the old value if existent.
    old_value = resolve_leaf(last_parent.get(name))

    # Update the value.
    new_value = modifier(*old_value)
    last_parent[name] = _merge_leaf(old_value, new_value)

    return root


def ensure(
    struct: Structure,
    path: PathLike,
    content: AbstractContent = None,
    file_op: FileOp = create,
) -> Structure:
    """Ensure a file exists in the representation of the project tree
    with the provided content.
    All the parent directories are automatically created.

    Args:
        struct: project representation as (possibly) nested.

        path: path-like string or object relative to the structure root.
            See :obj:`~.modify`.

            .. versionchanged:: 4.0
               The function no longer accepts a list of strings of path parts.

        content: file text contents, ``None`` by default.
            The old content is preserved if ``None``.

        file_op: see :obj:`pyscaffold.operations`, :obj:`~.create`` by default.

    .. versionchanged:: 4.0
       Instead of a ``update_rule`` flag, the function now accepts a :obj:`file_op
       <pyscaffold.oprtations.FileOp>`.

    Returns:
        Updated project tree representation

    Note:
        Use an empty string as content to ensure a file is created empty.
    """
    return modify(
        struct, path, lambda old, _: (old if content is None else content, file_op)
    )


def reject(struct: Structure, path: PathLike) -> Structure:
    """Remove a file from the project tree representation if existent.

    Args:
        struct: project representation as (possibly) nested.

        path: path-like string or object relative to the structure root.
            See :obj:`~.modify`.

            .. versionchanged:: 4.0
               The function no longer accepts a list of strings of path parts.

    Returns:
        Modified project tree representation
    """
    # Retrieve a list of parts from a path-like object
    path_parts = Path(path).parts

    # Walk the entire path, creating parents if necessary.
    root = deepcopy(struct)
    last_parent: dict = root
    name = path_parts[-1]
    for parent in path_parts[:-1]:
        if parent not in last_parent:
            return root  # one ancestor already does not exist, do nothing
        last_parent = last_parent[parent]

    if name in last_parent:
        del last_parent[name]

    return root


def merge(old: Structure, new: Structure) -> Structure:
    """Merge two dict representations for the directory structure.

    Basically a deep dictionary merge, except from the leaf update method.

    Args:
        old: directory descriptor that takes low precedence during the merge.
        new: directory descriptor that takes high precedence during the merge.


    .. versionchanged:: 4.0
        Project structure now considers everything **under** the
        top level project folder.

    Returns:
        Resulting merged directory representation

    Note:
        Use an empty string as content to ensure a file is created empty.
        (``None`` contents will not be created).
    """
    return _inplace_merge(deepcopy(old), new)


def _inplace_merge(old: Structure, new: Structure) -> Structure:
    """Similar to :obj:`~.merge` but modifies the first dict."""

    for key, value in new.items():
        old_value = old.get(key, None)
        new_is_dict = isinstance(value, dict)
        old_is_dict = isinstance(old_value, dict)
        if new_is_dict and old_is_dict:
            old[key] = _inplace_merge(
                cast(Structure, old_value), cast(Structure, value)
            )
        elif old_value is not None and not new_is_dict and not old_is_dict:
            # both are defined and final leaves
            old[key] = _merge_leaf(cast(Leaf, old_value), cast(Leaf, value))
        else:
            old[key] = deepcopy(value)

    return old


def _merge_leaf(old_value: Leaf, new_value: Leaf) -> Leaf:
    """Merge leaf values for the directory tree representation.

    The leaf value is expected to be a tuple ``(content, update_rule)``.
    When a string is passed, it is assumed to be the content and
    ``None`` is used for the update rule.

    Args:
        old_value: descriptor for the file that takes low precedence during the merge.
        new_value: descriptor for the file that takes high precedence during the merge.

    Note:
        ``None`` contents are ignored, use and empty string to force empty
        contents.

    Returns:
        Resulting value for the merged leaf
    """
    old = old_value if isinstance(old_value, (list, tuple)) else (old_value, None)
    new = new_value if isinstance(new_value, (list, tuple)) else (new_value, None)

    content = old[0] if new[0] is None else new[0]
    file_op = old[1] if new[1] is None else new[1]

    if file_op is None:
        return content

    return (content, file_op)
