""" configuration """
from __future__ import print_function, unicode_literals
import os
import re
import warnings

from .utils import trace

DEFAULT_TAG_REGEX = r"^(?:[\w-]+-)?(?P<version>[vV]?\d+(?:\.\d+){0,2}[^\+]+)(?:\+.*)?$"
DEFAULT_VERSION_SCHEME = "version_scheme"


def _check_tag_regex(value):
    if not value:
        value = DEFAULT_TAG_REGEX
    regex = re.compile(value)

    group_names = regex.groupindex.keys()
    if regex.groups == 0 or (regex.groups > 1 and "version" not in group_names):
        warnings.warn(
            "Expected tag_regex to contain a single match group or a group named"
            " 'version' to identify the version part of any tag."
        )

    return regex


def _check_absolute_root(root, relative_to):
    if relative_to:
        if os.path.isabs(root) and not root.startswith(relative_to):
            warnings.warn(
                "absolute root path '%s' overrides relative_to '%s'"
                % (root, relative_to)
            )
        root = os.path.join(os.path.dirname(relative_to), root)
    return os.path.abspath(root)


class Configuration(object):
    """ Global configuration model """

    _root = None
    version_scheme = None
    local_scheme = None
    write_to = None
    write_to_template = None
    _relative_to = None
    parse = None
    _tag_regex = None
    _absolute_root = None

    def __init__(self, relative_to=None, root="."):
        # TODO:
        self._relative_to = relative_to
        self._root = "."

        self.root = root
        self.version_scheme = DEFAULT_VERSION_SCHEME
        self.local_scheme = "node-and-date"
        self.write_to = ""
        self.write_to_template = None
        self.parse = None
        self.tag_regex = DEFAULT_TAG_REGEX

    @property
    def absolute_root(self):
        return self._absolute_root

    @property
    def relative_to(self):
        return self._relative_to

    @relative_to.setter
    def relative_to(self, value):
        self._absolute_root = _check_absolute_root(self._root, value)
        self._relative_to = value
        trace("root", repr(self._absolute_root))

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._absolute_root = _check_absolute_root(value, self._relative_to)
        self._root = value
        trace("root", repr(self._absolute_root))

    @property
    def tag_regex(self):
        return self._tag_regex

    @tag_regex.setter
    def tag_regex(self, value):
        self._tag_regex = _check_tag_regex(value)
