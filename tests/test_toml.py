from collections.abc import MutableMapping
from textwrap import dedent

from pyscaffold import toml


def test_dumps():
    serialised = toml.dumps({"test": {"key": 42}})
    assert isinstance(serialised, str)
    assert "[test]" in serialised
    assert "key = 42" in serialised

    unserialised = toml.loads(serialised)
    assert "test" in unserialised
    assert "key" in unserialised["test"]
    assert unserialised["test"]["key"] == 42


def test_loads():
    example = """\
    [test]
    key = 42
    list = [1, 2, 3, 4]

    [nested.table.nested]
    x = "y"
    """

    unserialised = toml.loads(dedent(example))

    assert isinstance(unserialised, MutableMapping)
    assert "test" in unserialised
    assert "key" in unserialised["test"]
    assert unserialised["test"]["key"] == 42
    assert unserialised["nested"]["table"]["nested"]["x"] == "y"
    assert unserialised["test"]["list"] == [1, 2, 3, 4]

    serialised = toml.dumps(unserialised)
    assert "[test]" in serialised
    assert "key = 42" in serialised


def test_setdefault():
    x = {}
    toml.setdefault(x, "a.b.c.d", 42)
    assert x["a"]["b"]["c"]["d"] == 42

    y = toml.loads(toml.dumps({}))
    assert "a" not in y
    toml.setdefault(y, "a.b.c.d", 42)
    assert y["a"]["b"]["c"]["d"] == 42

    # When key is already set, setdefault returns the existing value
    # and do not change the object
    assert toml.setdefault(y, "a.b.c.d", -1) == 42
    assert y["a"]["b"]["c"]["d"] == 42
