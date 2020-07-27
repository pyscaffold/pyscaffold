"""Functions that extend (or tap into) the behaviour of Python's stdlib or for
manipulating/handling built-in data structures.
"""


def setdefault(dict_ref, key, value):
    """Equivalent to built-in :meth:`dict.setdefault`, but ignores values
    if ``None`` or ``""`` (both existing in the dictionary or as the ``value``
    to set).

    Modifies the original dict and returns a reference to it
    """
    if key in dict_ref and dict_ref[key] not in (None, ""):
        return dict_ref
    if value in (None, ""):
        return dict_ref
    dict_ref[key] = value
    return dict_ref
