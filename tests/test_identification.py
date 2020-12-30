from unittest.mock import Mock

import pytest

from pyscaffold.exceptions import InvalidIdentifier
from pyscaffold.identification import (
    dasherize,
    deterministic_name,
    deterministic_sort,
    get_id,
    is_valid_identifier,
    levenshtein,
    make_valid_identifier,
    underscore,
)


def test_is_valid_identifier():
    bad_names = [
        "has whitespace",
        "has-hyphen",
        "has_special_char$",
        "1starts_with_digit",
    ]
    for bad_name in bad_names:
        assert not is_valid_identifier(bad_name)
    valid_names = ["normal_variable_name", "_private_var", "_with_number1"]
    for valid_name in valid_names:
        assert is_valid_identifier(valid_name)


def test_make_valid_identifier():
    assert make_valid_identifier("has whitespaces ") == "has_whitespaces"
    assert make_valid_identifier("has-hyphon") == "has_hyphon"
    assert make_valid_identifier("special chars%") == "special_chars"
    assert make_valid_identifier("UpperCase") == "uppercase"
    with pytest.raises(InvalidIdentifier):
        make_valid_identifier("def")


def test_levenshtein():
    s1 = "born"
    s2 = "burn"
    assert levenshtein(s1, s2) == 1
    s2 = "burnt"
    assert levenshtein(s1, s2) == 2
    assert levenshtein(s2, s1) == 2
    s2 = ""
    assert levenshtein(s2, s1) == 4


def test_dasherize():
    assert dasherize("hello_world") == "hello-world"
    assert dasherize("helloworld") == "helloworld"
    assert dasherize("") == ""


def test_underscore():
    assert underscore("HelloWorld") == "hello_world"
    assert underscore("Hello-World") == "hello_world"
    assert underscore("Hello   World") == "hello_world"
    assert underscore("Hello---World") == "hello_world"
    assert underscore("HelLo-WorLd") == "hel_lo_wor_ld"
    assert underscore("helloworld") == "helloworld"
    assert underscore("PYTHON") == "p_y_t_h_o_n"
    assert underscore("") == ""


@pytest.mark.parametrize(
    "obj, name",
    [
        (underscore, "pyscaffold.identification.underscore"),
        (None, "...NoneType"),
        (InvalidIdentifier(), "pyscaffold.exceptions.InvalidIdentifier"),
    ],
)
def test_deterministic_name(obj, name):
    assert deterministic_name(obj) == name


def test_deterministic_sort():
    ex = InvalidIdentifier()
    ext1 = Mock(__module__="pyscaffold.extension", __qualname__="Extension")
    ext2 = Mock(__module__="pyscaffoldext", __qualname__="Extension")
    assert deterministic_sort([underscore, None, ext2, ext1, ex]) == [
        None,
        ex,
        ext1,
        underscore,
        ext2,
    ]


def test_get_id():
    def custom_action(structure, options):
        return structure, options

    custom_action.__module__ = "awesome_module"
    assert get_id(custom_action) == "awesome_module:custom_action"
