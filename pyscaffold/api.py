# -*- coding: utf-8 -*-
"""
Exposed API for accessing PyScaffold via Python.
"""
from __future__ import absolute_import, print_function

import os
from os.path import exists as path_exists
from os.path import join as join_path

from six import string_types

from .structure import FileOp

__author__ = "Anderson Bravalheri"
__license__ = "new BSD"


class Scaffold(FileOp):
    """Representation of the actions performed by the ``putup`` command.

    Args:
        options (dict): dict with all PyScaffold options, including the ones
            parsed from command line

    Attributes:
        options (dict): dict with all PyScaffold options, including the ones
            parsed from command line
        before_generate ([function]): array filled with functions that will be
            executed **before** the generation of files
        after_generate ([function]): array filled with functions that will be
            executed **after** the generation of files
        structure (dict): directory tree representation as a (possibly nested)
            dictionary.
            The keys indicate the path where a file will be generated,
            while the value indicates the content.
            Additionally, tuple values are allowed in order to specify the
            rule that will be followed during an ``update`` operation
            (see :class:`~.FileOp`).
            In this case, the first element is the file content and the second
            element is the update rule. For example, the dictionary::

                {'project': {
                    'namespace': {
                        'module.py': ('print("Hello World!")',
                                      Scaffold.NO_UPDATE)}}

            represents a ``project/namespace/module.py`` file with content
            ``print("Hello World!")``, that will be created only if not
            present.

    Note:
        :attr:`~Scaffold.before_generate` and :attr:`~Scaffold.after_generate`
        hooks should be defined as a function of a single argument,
        the :class:`Scaffold` instance itself.
    """

    def __init__(self, options, structure=None,
                 before_generate=None, after_generate=None):
        self.options = options
        self.structure = structure or {}
        self.before_generate = before_generate or []
        self.after_generate = after_generate or []

    def merge_structure(self, extra_files):
        """Deep merge the given structure representation with the current one.

        Args:
            extra_files (dict): directory tree representation as a
                                (possibly nested) dictionary

        Note:
            Use an empty string as content to ensure a file is created empty.
        """
        self.structure = _merge_structure(self.structure, extra_files)

    def ensure_file(self, name, content=None, update_rule=None, path=[]):
        """Ensure a file exists in the current representation of the file tree.
        All the parent directories are automatically created.

        Args:
            filename (str): basename of the file that will be created
            content (str): its text contents
            update_rule: see :class:`~.FileOp`, ``None`` by default
            path (list): ancestors of the file, ordered from the working
                directory to the parent folder (empty by default)

        Note:
            Use an empty string as content to ensure a file is created empty.
        """
        # Ensure path is a list.
        if isinstance(path, string_types):
            path = path.split('/')

        # Walk the entire path, creating parents if necessary.
        last_parent = self.structure
        for parent in path:
            if parent not in last_parent:
                last_parent[parent] = {}
            last_parent = last_parent[parent]

        # Get the old value if existent.
        old_value = last_parent.get(name, (None, None))

        # Update the value.
        new_value = (content, update_rule)
        last_parent[name] = _merge_file_leaf(old_value, new_value)

    @property
    def filtered_structure(self):
        """dict: representation of the directory tree, but only containing
        files that actually will be written to disc.

        All the leaves are strings with contents of the files
        (no update rule is present).
        # TODO: implement
        """
        return _filter_structure(self.structure, self.options)


# -------- Auxiliary functions --------


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
        tuple: resulting value for the merged leaf
    """
    if not isinstance(old_value, (list, tuple)):
        old_value = (old_value, None)
    if not isinstance(new_value, (list, tuple)):
        new_value = (new_value, None)

    content = new_value[0] if new_value[0] is not None else old_value[0]
    rule = new_value[1] if new_value[1] is not None else old_value[1]

    return (content, rule)


def _merge_structure(old, new):
    """Merge two dict representations for the directory structure.

    Basically a deep dictionary merge, except from the leaf update method.
    Note that the `old` dict is modified in the process.

    Args:
        old (dict): directory descriptor that takes low precedence
                    during the merge
        new (dict): directory descriptor that takes high precedence
                    during the merge

    Returns:
        dict: resulting merged directory representation
    """
    for key, value in new.items():
        old_value = old.get(key, None)
        new_is_dict = isinstance(value, dict)
        old_is_dict = isinstance(old_value, dict)
        if new_is_dict and old_is_dict:
            old[key] = _merge_structure(old_value, value)
        elif old_value is not None and not new_is_dict and not old_is_dict:
            # both are defined and final leaves
            old[key] = _merge_file_leaf(old_value, value)
        else:
            old[key] = value

    return old


def _filter_structure(structure, options, path=None):
    """Filter the structure, leaving only files that actually will be written.

    This function applies the update rules when necessary.

    Args:
        structure (dict): directory tree described as a dict (see
            :attr:`Scaffold.structure`). Each leaf can be just a string or a
            tuple containing an update rule.
        options (dict): dict with all PyScaffold options, including the ones
            parsed from command line

    Returns:
        dict: also a directory tree representation, but all the leaves are
        plain strings (no update rule is present).
    """
    if not path:
        path = [os.getcwd()]

    filtered_structure = {}

    for key, value in structure.items():
        if isinstance(value, dict):  # nested dir
            value = _filter_structure(value, options, path + [key])
        else:  # file
            full_path = join_path(*path, key)
            value = _apply_update_rule(full_path, value, options)

        if value:  # avoids inserting empty dirs and empty files
            filtered_structure[key] = value

    return filtered_structure


def _apply_update_rule(path, value, options):
    """Returns the content of the file if it should be generated,
    or None otherwise.

    Args:
        path (str): complete file for the path
        value (tuple or str): content (and update rule)
        options (dict): options from PyScaffold
    """
    if isinstance(value, (tuple, list)):
        content, rule = value
    else:
        content, rule = value, None

    skip = options['update'] and not options['force'] and (
            rule == Scaffold.NO_CREATE or
            path_exists(path) and rule == Scaffold.NO_OVERWRITE)

    return None if skip else content
