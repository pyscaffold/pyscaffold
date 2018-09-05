# -*- coding: utf-8 -*-
"""
Useful functions for manipulating the action list and project structure.
"""

from copy import deepcopy
from pathlib import PurePath

from ..exceptions import ActionNotFound
from ..log import logger
from ..structure import FileOp, define_structure
from ..utils import get_id

logger = logger  # Sphinx workaround to force documenting imported members
"""Logger wrapper, that provides methods like :obj:`~.ReportLogger.report`.
See :class:`~.ReportLogger`.
"""

NO_OVERWRITE = FileOp.NO_OVERWRITE
"""Do not overwrite an existing file during update
(still created if not exists)
"""

NO_CREATE = FileOp.NO_CREATE
"""Do not create the file during an update"""


# -------- Project Structure --------

def _id_func(x):
    """Identity function"""
    return x


def modify(struct, path, modifier=_id_func, update_rule=None):
    """Modify the contents of a file in the representation of the project tree.

    If the given path, does not exist the parent directories are automatically
    created.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`. See :obj:`~.merge`.

        path (os.PathLike): path-like string or object relative to the
            structure root. The following examples are equivalent::

                from pathlib import PurePath

                'docs/api/index.html'
                PurePath('docs', 'api', 'index.html')

            *Deprecated* - Alternatively, a list with the parts of the path can
            be provided, ordered from the structure root to the file itself.

        modifier (callable): function (or callable object) that receives the
            old content as argument and returns the new content.
            If no modifier is passed, the identity function will be used.
            Note that, if the file does not exist in ``struct``, ``None`` will
            be passed as argument. Example::

                modifier = lambda old: (old or '') + 'APPENDED CONTENT'!
                modifier = lambda old: 'PREPENDED CONTENT!' + (old or '')

        update_rule: see :class:`~.FileOp`, ``None`` by default.
            Note that, if no ``update_rule`` is passed, the previous one is
            kept.

    Returns:
        dict: updated project tree representation

    Note:
        Use an empty string as content to ensure a file is created empty
        (``None`` contents will not be created).

    Warning:
        *Deprecation Notice* - In the next major release, the usage of lists
        for the ``path`` argument will result in an error. Please use
        :obj:`pathlib.PurePath` instead.
    """
    # Retrieve a list of parts from a path-like object
    if isinstance(path, (list, tuple)):
        path_parts = path
    else:
        # TODO: Remove conditional for v4 (always do the following)
        path_parts = PurePath(path).parts

    # Walk the entire path, creating parents if necessary.
    root = deepcopy(struct)
    last_parent = root
    name = path_parts[-1]
    for parent in path_parts[:-1]:
        last_parent = last_parent.setdefault(parent, {})

    # Get the old value if existent.
    old_value = last_parent.get(name, (None, None))
    if not isinstance(old_value, (list, tuple)):
        old_value = (old_value, None)

    # Update the value.
    new_value = (modifier(old_value[0]), update_rule)
    last_parent[name] = _merge_file_leaf(old_value, new_value)

    return root


def ensure(struct, path, content=None, update_rule=None):
    """Ensure a file exists in the representation of the project tree
    with the provided content.
    All the parent directories are automatically created.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`. See :obj:`~.merge`.

        path (os.PathLike): path-like string or object relative to the
            structure root. The following examples are equivalent::

                from pathlib import PurePath

                'docs/api/index.html'
                PurePath('docs', 'api', 'index.html')

            *Deprecated* - Alternatively, a list with the parts of the path can
            be provided, ordered from the structure root to the file itself.

        content (str): file text contents, ``None`` by default.
            The old content is preserved if ``None``.

        update_rule: see :class:`~.FileOp`, ``None`` by default

    Returns:
        dict: updated project tree representation

    Note:
        Use an empty string as content to ensure a file is created empty.

    Warning:
        *Deprecation Notice* - In the next major release, the usage of lists
        for the ``path`` argument will result in an error. Please use
        :obj:`pathlib.PurePath` instead.
    """
    modifier = _id_func if content is None else (lambda _: content)
    return modify(struct, path, modifier, update_rule)


def reject(struct, path):
    """Remove a file from the project tree representation if existent.

    Args:
        struct (dict): project representation as (possibly) nested
            :obj:`dict`. See :obj:`~.merge`.

        path (os.PathLike): path-like string or object relative to the
            structure root. The following examples are equivalent::

                from pathlib import PurePath

                'docs/api/index.html'
                PurePath('docs', 'api', 'index.html')

            *Deprecated* - Alternatively, a list with the parts of the path can
            be provided, ordered from the structure root to the file itself.

    Returns:
        dict: modified project tree representation

    Warning:
        *Deprecation Notice* - In the next major release, the usage of lists
        for the ``path`` argument will result in an error. Please use
        :obj:`pathlib.PurePath` instead.
    """
    # Retrieve a list of parts from a path-like object
    if isinstance(path, (list, tuple)):
        path_parts = path
    else:
        # TODO: Remove conditional for v4 (always do the following)
        path_parts = PurePath(path).parts

    # Walk the entire path, creating parents if necessary.
    root = deepcopy(struct)
    last_parent = root
    name = path_parts[-1]
    for parent in path_parts[:-1]:
        if parent not in last_parent:
            return root  # one ancestor already does not exist, do nothing
        last_parent = last_parent[parent]

    if name in last_parent:
        del last_parent[name]

    return root


def merge(old, new):
    """Merge two dict representations for the directory structure.

    Basically a deep dictionary merge, except from the leaf update method.

    Args:
        old (dict): directory descriptor that takes low precedence
                    during the merge
        new (dict): directory descriptor that takes high precedence
                    during the merge

    The directory tree is represented as a (possibly nested) dictionary.
    The keys indicate the path where a file will be generated, while the
    value indicates the content.  Additionally, tuple values are allowed in
    order to specify the rule that will be followed during an ``update``
    operation (see :class:`~.FileOp`).  In this case, the first element is
    the file content and the second element is the update rule. For
    example, the dictionary::

        {'project': {
            'namespace': {
                'module.py': ('print("Hello World!")',
                              helpers.NO_OVERWRITE)}}

    represents a ``project/namespace/module.py`` file with content
    ``print("Hello World!")``, that will be created only if not
    present.

    Returns:
        dict: resulting merged directory representation

    Note:
        Use an empty string as content to ensure a file is created empty.
        (``None`` contents will not be created).
    """
    return _inplace_merge(deepcopy(old), new)


def _inplace_merge(old, new):
    """Similar to :obj:`~.merge` but modifies the first dict."""

    for key, value in new.items():
        old_value = old.get(key, None)
        new_is_dict = isinstance(value, dict)
        old_is_dict = isinstance(old_value, dict)
        if new_is_dict and old_is_dict:
            old[key] = _inplace_merge(old_value, value)
        elif old_value is not None and not new_is_dict and not old_is_dict:
            # both are defined and final leaves
            old[key] = _merge_file_leaf(old_value, value)
        else:
            old[key] = deepcopy(value)

    return old


def _merge_file_leaf(old_value, new_value):
    """Merge leaf values for the directory tree representation.

    The leaf value is expected to be a tuple ``(content, update_rule)``.
    When a string is passed, it is assumed to be the content and
    ``None`` is used for the update rule.

    Args:
        old_value (tuple or str): descriptor for the file that takes low
                                  precedence during the merge
        new_value (tuple or str): descriptor for the file that takes high
                                  precedence during the merge

    Note:
        ``None`` contents are ignored, use and empty string to force empty
        contents.

    Returns:
        tuple or str: resulting value for the merged leaf
    """
    if not isinstance(old_value, (list, tuple)):
        old_value = (old_value, None)
    if not isinstance(new_value, (list, tuple)):
        new_value = (new_value, None)

    content = new_value[0] if new_value[0] is not None else old_value[0]
    rule = new_value[1] if new_value[1] is not None else old_value[1]

    if rule is None:
        return content

    return (content, rule)


# -------- Action List --------

def register(actions, action, before=None, after=None):
    """Register a new action to be performed during scaffold.

    Args:
        actions (list): previous action list.
        action (callable): function with two arguments: the first one is a
            (nested) dict representing the file structure of the project
            and the second is a dict with scaffold options.
            This function **MUST** return a tuple with two elements similar
            to its arguments. Example::

                def do_nothing(struct, opts):
                    return (struct, opts)

        **kwargs (dict): keyword arguments make it possible to choose a
            specific order when executing actions: when ``before`` or
            ``after`` keywords are provided, the argument value is used as
            a reference position for the new action. Example::

                helpers.register(actions, do_nothing,
                                 after='create_structure')
                    # Look for the first action with a name
                    # `create_structure` and inserts `do_nothing` after it.
                    # If more than one registered action is named
                    # `create_structure`, the first one is selected.

                helpers.register(
                    actions, do_nothing,
                    before='pyscaffold.structure:create_structure')
                    # Similar to the previous example, but the probability
                    # of name conflict is decreased by including the module
                    # name.

            When no keyword argument is provided, the default execution
            order specifies that the action will be performed after the
            project structure is defined, but before it is written to the
            disk. Example::


                helpers.register(actions, do_nothing)
                    # The action will take place after
                    # `pyscaffold.structure:define_structure`

    Returns:
        list: modified action list.
    """
    reference = before or after or get_id(define_structure)
    position = _find(actions, reference)
    if not before:
        position += 1

    clone = actions[:]
    clone.insert(position, action)

    return clone


def unregister(actions, reference):
    """Prevent a specific action to be executed during scaffold.

    Args:
        actions (list): previous action list.
        reference (str): action identifier. Similarly to the keyword
            arguments of :obj:`~.register` it can assume two formats:

                - the name of the function alone,
                - the name of the module followed by ``:`` and the name
                  of the function

    Returns:
        list: modified action list.
    """
    position = _find(actions, reference)
    return actions[:position] + actions[position+1:]


def _find(actions, name):
    """Find index of name in actions"""
    if ':' in name:
        names = [get_id(action) for action in actions]
    else:
        names = [action.__name__ for action in actions]

    try:
        return names.index(name)
    except ValueError:
        raise ActionNotFound(name)
