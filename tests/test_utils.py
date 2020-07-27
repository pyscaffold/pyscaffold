from pyscaffold import utils


def test_setdefault():
    # Given a dict with some 'empty' fields
    adict = {"a": None, "b": "", "c": False, "d": "hello"}
    # When we use setdefault in those fields
    utils.setdefault(adict, "a", 42)
    utils.setdefault(adict, "b", "world")
    # Then the values should change
    assert adict["a"] == 42
    assert adict["b"] == "world"
    # The same is valid for non existing fields
    utils.setdefault(adict, "42", "world")
    assert adict["42"] == "world"
    # But meaninful values (including False) should not change
    utils.setdefault(adict, "c", True)
    utils.setdefault(adict, "d", "world")
    assert adict["c"] is False
    assert adict["d"] == "hello"
