import logging
import re

from pkg_resources import parse_version

import pytest

from pyscaffold import utils
from pyscaffold.exceptions import InvalidIdentifier
from pyscaffold.log import logger


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


def test_exceptions2exit():
    @utils.exceptions2exit([RuntimeError])
    def func(_):
        raise RuntimeError("Exception raised")

    with pytest.raises(SystemExit):
        func(1)


def test_exceptions2exit_verbose(capsys):
    @utils.exceptions2exit([RuntimeError])
    def func(_):
        logger.level = logging.DEBUG
        raise RuntimeError("Exception raised")

    with pytest.raises(SystemExit):
        func(1)
    error = capsys.readouterr().err
    match = re.search(r"raise RuntimeError", error)
    assert match


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


def test_is_dep_included():
    deps = {"setuptools_scm": "some.version", "pyscaffold": "42.0", "django": "0"}
    assert utils.is_dep_included("setuptools_scm>=34", deps)
    assert utils.is_dep_included("pyscaffold>=5.34.5,<=42", deps)
    assert utils.is_dep_included("django", deps)
    assert not utils.is_dep_included("appdirs==1", deps)
    assert not utils.is_dep_included("cookiecutter<8", deps)
    assert not utils.is_dep_included("mypkg~=9.0", deps)


def test_split_deps():
    assert utils.split_deps(
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    appdirs==1"
        "\n    cookiecutter<8"
        "\n    mypkg~=9.0"
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert utils.split_deps(
        "\n    pyscaffold>=42.1.0,<43.0;appdirs==1"
        "\n    cookiecutter<8;mypkg~=9.0\n\n"
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert utils.split_deps(
        "pyscaffold>=42.1.0,<43.0; appdirs==1; cookiecutter<8; mypkg~=9.0; "
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]


def test_remove_deps():
    assert utils.remove_deps(
        ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        ["appdirs"],
    ) == ["pyscaffold>=42.1.0,<43.0", "cookiecutter<8", "mypkg~=9.0"]
    assert utils.remove_deps(
        ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        {"mypkg": 0},
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8"]


def test_get_requirements_str():
    own_deps = {
        "setuptools_scm": parse_version("1.2.5"),
        "pyscaffold": parse_version("42.1.0"),
        "django": parse_version("5.3.99999"),
    }
    # No intersection
    assert utils.get_requirements_str(
        ["appdirs==1", "cookiecutter<8", "mypkg~=9.0"], own_deps
    ) == (
        "\n    setuptools_scm>=1.2.5,<2.0"
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    django>=5.3.99999,<6.0"
        "\n    appdirs==1"
        "\n    cookiecutter<8"
        "\n    mypkg~=9.0"
    )
    # With intersection => own_deps win
    assert utils.get_requirements_str(
        ["appdirs==1", "pyscaffold<8", "mypkg~=9.0"], own_deps
    ) == (
        "\n    setuptools_scm>=1.2.5,<2.0"
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    django>=5.3.99999,<6.0"
        "\n    appdirs==1"
        "\n    mypkg~=9.0"
    )
