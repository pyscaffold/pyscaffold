import pytest

from pyscaffold import utils
from pyscaffold.exceptions import InvalidIdentifier


def test_is_valid_identifier():
    bad_names = [
        "has whitespace",
        "has-hyphen",
        "has_special_char$",
        "1starts_with_digit",
    ]
    for bad_name in bad_names:
        assert not utils.is_valid_identifier(bad_name)
    valid_names = ["normal_variable_name", "_private_var", "_with_number1"]
    for valid_name in valid_names:
        assert utils.is_valid_identifier(valid_name)


def test_make_valid_identifier():
    assert utils.make_valid_identifier("has whitespaces ") == "has_whitespaces"
    assert utils.make_valid_identifier("has-hyphon") == "has_hyphon"
    assert utils.make_valid_identifier("special chars%") == "special_chars"
    assert utils.make_valid_identifier("UpperCase") == "uppercase"
    with pytest.raises(InvalidIdentifier):
        utils.make_valid_identifier("def")


def test_levenshtein():
    s1 = "born"
    s2 = "burn"
    assert utils.levenshtein(s1, s2) == 1
    s2 = "burnt"
    assert utils.levenshtein(s1, s2) == 2
    assert utils.levenshtein(s2, s1) == 2
    s2 = ""
    assert utils.levenshtein(s2, s1) == 4


def test_dasherize():
    assert utils.dasherize("hello_world") == "hello-world"
    assert utils.dasherize("helloworld") == "helloworld"
    assert utils.dasherize("") == ""


def test_underscore():
    assert utils.underscore("HelloWorld") == "hello_world"
    assert utils.underscore("Hello-World") == "hello_world"
    assert utils.underscore("Hello   World") == "hello_world"
    assert utils.underscore("Hello---World") == "hello_world"
    assert utils.underscore("HelLo-WorLd") == "hel_lo_wor_ld"
    assert utils.underscore("helloworld") == "helloworld"
    assert utils.underscore("PYTHON") == "p_y_t_h_o_n"
    assert utils.underscore("") == ""


def test_get_id():
    def custom_action(structure, options):
        return structure, options

    custom_action.__module__ = "awesome_module"
    assert utils.get_id(custom_action) == "awesome_module:custom_action"
