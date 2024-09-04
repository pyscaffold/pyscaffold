"""Thin wrapper around the dependency so we can maintain some stability while being able
to swap implementations (e.g. replace `tomlkit`_ with `toml`_).

`tomlkit`_ is preferred because it supports comments.

.. _tomlkit: https://github.com/sdispater/tomlkit
.. _toml: https://github.com/uiri/toml
"""

from typing import Any, List, MutableMapping, NewType, Tuple, TypeVar, Union, cast

import tomlkit

TOMLMapping = NewType("TOMLMapping", MutableMapping)
"""Abstraction on the value returned by :obj:`loads`.

This kind of object ideally should present a dict-like interface and be able to preserve
the formatting and comments of the original TOML file.
"""

T = TypeVar("T")


def loads(text: str) -> TOMLMapping:
    """Parse a string containing TOML into a dict-like object,
    preserving style somehow.
    """
    return TOMLMapping(cast(MutableMapping, tomlkit.loads(text)))


def dumps(obj: Union[TOMLMapping, dict]) -> str:
    # and do not change the object
    # TODO: If/when tomlkit allows serialising arbitrary Mapping objects, replace union
    #       with Mapping
    """Serialize a dict-like object into a TOML str,
    If the object was generated via :obj:`loads`, then the style will be preserved.
    """
    return tomlkit.dumps(obj)  # type: ignore[arg-type]
    # TODO: Once tomlkit improves dumps' type hints, remove type ignore comment


def setdefault(obj: MutableMapping, key: str, value: T) -> T:
    # TODO: Use recursive type for obj, when available in mypy, and remove type: ignore
    """tomlkit seems to be tricky to use together with setdefault, this function is a
    workaround for that.

    When ``key`` is string containing ``'.'``, it will perform a nested setdefault.
    """
    keys = key.split(".")
    items: List[Tuple[str, Any]] = list(zip(keys, [{}] * len(keys)))
    items[-1] = (keys[-1], value)

    last = obj
    for key, value in items:
        if key not in last:
            last[key] = value
        last = last[key]  # type: ignore

    return cast(T, last)
