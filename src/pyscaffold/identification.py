"""Internal library for manipulating, creating and dealing with names, or more generally
identifiers.
"""

import keyword
import re

from .exceptions import InvalidIdentifier


def is_valid_identifier(string):
    """Check if string is a valid package name

    Args:
        string (str): package name

    Returns:
        bool: True if string is valid package name else False
    """
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False
    return True


def make_valid_identifier(string):
    """Try to make a valid package name identifier from a string

    Args:
        string (str): invalid package name

    Returns:
        str: valid package name as string or :obj:`RuntimeError`

    Raises:
        :obj:`InvalidIdentifier`: raised if identifier can not be converted
    """
    string = str(string).strip()
    string = string.replace("-", "_")
    string = string.replace(" ", "_")
    string = re.sub("[^_a-zA-Z0-9]", "", string)
    string = string.lower()
    if is_valid_identifier(string):
        return string

    raise InvalidIdentifier("String cannot be converted to a valid identifier.")


# from http://en.wikibooks.org/, Creative Commons Attribution-ShareAlike 3.0
def levenshtein(s1, s2):
    """Calculate the Levenshtein distance between two strings

    Args:
        s1 (str): first string
        s2 (str): second string

    Returns:
        int: distance between s1 and s2
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def dasherize(word: str) -> str:
    """Replace underscores with dashes in the string.

    Example::

        >>> dasherize("foo_bar")
        "foo-bar"

    Args:
        word (str): input word

    Returns:
        input word with underscores replaced by dashes
    """
    return word.replace("_", "-")


CAMEL_CASE_SPLITTER = re.compile(r"\W+|([A-Z][^A-Z\W]*)")


def underscore(word: str) -> str:
    """Convert CamelCasedStrings or dasherized-strings into underscore_strings.

    Example::

        >>> underscore("FooBar-foo")
        "foo_bar_foo"
    """
    return "_".join(w for w in CAMEL_CASE_SPLITTER.split(word) if w).lower()


def deterministic_name(obj):
    """Private API that returns an string that can be used to deterministically
    deduplicate and sort sequences of objects.
    """
    mod_name = getattr(obj, "__module__", "..")
    qual_name = getattr(obj, "__qualname__", obj.__class__.__qualname__)
    return f"{mod_name}.{qual_name}"


def deterministic_sort(sequence):
    """Private API that order a sequence of objects lexicographically (by
    :obj:`deterministic_name`), removing duplicates, which is needed for determinism.

    The main purpose of this function tis to deterministically sort a sequence of
    PyScaffold extensions (it will also sort internal extensions before external:
    "pyscaffold.*" < "pyscaffoldext.*").
    """
    deduplicated = {deterministic_name(x): x for x in sequence}
    # ^  duplicated keys will overwrite each other, so just one of them is left
    return [v for (_k, v) in sorted(deduplicated.items())]


def get_id(function):
    """Given a function, calculate its identifier.

    A identifier is a string in the format ``<module name>:<function name>``,
    similarly to the convention used for setuptools entry points.

    Note:
        This function does not return a Python 3 ``__qualname__`` equivalent.
        If the function is nested inside another function or class, the parent
        name is ignored.

    Args:
        function (callable): function object

    Returns:
        str: identifier
    """
    return "{}:{}".format(function.__module__, function.__name__)
