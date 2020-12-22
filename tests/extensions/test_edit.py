import argparse
from textwrap import dedent
from unittest.mock import Mock

from pyscaffold.extensions import edit

from ..helpers import ArgumentParser


def normalise(text: str) -> str:
    return "\n".join(text.strip().splitlines())


def test_wrap():
    text = "as eireir tueroue asdiuodsi usaoifdu asdouusa doudas"
    assert (
        normalise(edit.wrap(text, 20))
        == "as eireir tueroue\nasdiuodsi usaoifdu\nasdouusa doudas"
    )


def test_comment():
    assert edit.comment("a") == "# a"
    assert edit.comment("a\nb") == "# a\n# b"
    assert edit.comment("a\nb", indent_level=4) == "    # a\n    # b"
    assert edit.comment("a\nb", comment_mark=";") == "; a\n; b"


def test_join_block():
    assert edit.join_block("a", "", "") == "a"
    assert edit.join_block("", "", "c") == "c"
    assert normalise(edit.join_block("a", "", "c")) == "a\nc"
    assert normalise(edit.join_block("", "b", "c")) == "b\nc"
    assert normalise(edit.join_block("a", "b", "c")) == "a\nb\nc"


def test_long_option():
    for flags in (["-o", "--option"], ["--option", "-o"]):
        action = argparse.Action(flags, "dest")
        assert edit.long_option(action).strip() == "--option"


def test_alternative_flags():
    for flags in (["-o", "--option", "-b"], ["--option", "-b", "-o"]):
        action = argparse.Action(flags, "dest")
        text = edit.alternative_flags(action)
        assert "--option" not in text
        assert all([flag in text for flag in ("-o", "-b")])


def test_example_no_value():
    action = argparse.Action(["--option", "-o"], "option", nargs=0)
    parser = ArgumentParser()
    # When no value is available in opts, then it should be commented
    option_line = edit.example_no_value(parser, action, {})
    assert option_line.strip() == "# --option"
    # When option value is True, then it should not be commented
    option_line = edit.example_no_value(parser, action, {"option": True})
    assert option_line.strip() == "--option"
    # When an extension is available, then it should not be commented
    option_line = edit.example_no_value(
        parser, action, {"extensions": [Mock(flag="--option")]}
    )
    assert option_line.strip() == "--option"


def test_example_noargs_action():
    action = argparse.Action(["--option", "-o"], "option", nargs=0, help="do 42 things")
    parser = ArgumentParser()
    # When no value is available in opts, then it should be commented
    text = dedent(
        """\
        # --option
            # (or alternatively: -o)
            # do 42 things
        """
    )
    assert normalise(text) == normalise(edit.example_with_help(parser, action, {}))

    # When option value is True, then it should not be commented
    text = dedent(
        """\
        --option
            # (or alternatively: -o)
            # do 42 things
        """
    )
    assert normalise(text) == normalise(
        edit.example_with_help(parser, action, {"option": True})
    )


def make_action(
    flags=("--option", "-o"),
    dest="option",
    nargs=None,
    help="do 42 things",
    metavar="OPTION",
):
    return argparse.Action(flags, dest, nargs=nargs, help=help, metavar=metavar)


def test_example():
    parser = ArgumentParser()

    # Options with variable nargs
    action = make_action(nargs=1)
    assert edit.example(parser, action, {}).strip() == "# --option OPTION"
    assert edit.example(parser, action, {"option": 32}).strip() == "--option 32"

    action = make_action(nargs=3)
    assert edit.example(parser, action, {}).strip() == "# --option OPTION OPTION OPTION"
    assert (
        edit.example(parser, action, {"option": [32, 21, 5]}).strip()
        == "--option 32 21 5"
    )

    action = make_action(nargs="*")
    example = edit.example(parser, action, {}).strip()
    expected = ("# --option [OPTION [OPTION ...]]", "# --option [OPTION ...]")
    assert example in expected

    action = make_action(nargs="+")
    assert edit.example(parser, action, {}).strip() == "# --option OPTION [OPTION ...]"

    action = make_action(nargs="?")
    assert edit.example(parser, action, {}).strip() == "# --option [OPTION]"

    # Positional argument:
    action = argparse.Action([], "arg", nargs=1, metavar="ARGUMENT")
    assert edit.example(parser, action, {}).strip() == "# ARGUMENT"
    assert edit.example(parser, action, {"arg": "value"}).strip() == "value"


def test_all_examples():
    parser = ArgumentParser()
    actions = [
        make_action(nargs=1),
        make_action(["--abc"], "abc", metavar="ABC", help="Abc-foobarize your project"),
    ]
    text = dedent(
        """\
        --option 23
            # (or alternatively: -o)
            # do 42 things


        # --abc ABC
            # Abc-foobarize your project
        """
    )
    assert normalise(text) == normalise(
        edit.all_examples(parser, actions, {"option": 23})
    )
