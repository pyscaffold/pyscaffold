"""Thin wrapper around the dependency so we can maintain some stability while being able
to swap implementations (e.g. replace `tomlkit`_ with `toml`_).

Despite being used in `pep517`_, `toml`_ offers limited support for comments, so we
prefer `tomlkit`_.

.. tomlkit: https://github.com/sdispater/tomlkit
.. toml: https://github.com/uiri/toml
.. pep517: https://github.com/pypa/pep517
"""
from typing import (
    Any,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NewType,
    Tuple,
    TypeVar,
    Union,
)

import tomlkit

TOMLMapping = NewType("TOMLMapping", MutableMapping[str, Any])
T = TypeVar("T")


def loads(text: str) -> TOMLMapping:
    """Parse a string containing TOML into a dict-like object,
    preserving style somehow.
    """
    return TOMLMapping(tomlkit.loads(text))


def dumps(obj: Mapping[str, Any]) -> str:
    """Serialize a dict-like object into a TOML str,
    If the object was generated via :obj:`loads`, then the style will be preserved.
    """
    return tomlkit.dumps(obj)


def setdefault(
    obj: MutableMapping[str, Any], key: Union[str, List[str]], value: T
) -> T:
    """tomlkit seems to be tricky to use togheter with setdefault, this function is a
    workaroud for that.

    When ``key`` is a list, it will perform a nested setdefault.
    """
    keys = [key] if isinstance(key, str) else key
    values: Iterator[Tuple[str, Any]] = zip(keys, [{}] * (len(keys) - 1) + [value])
    # ^  fill parent values with an empty dict as default
    value = obj
    for k, v in values:
        if k not in value:
            value[k] = v
        value = value[k]

    return value
