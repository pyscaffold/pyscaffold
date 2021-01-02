import argparse
from textwrap import dedent
from unittest.mock import Mock

from pyscaffold import api, cli
from pyscaffold.extensions import config, interactive

from ..helpers import ArgumentParser


def normalise(text: str) -> str:
    return "\n".join(text.strip().splitlines())


def test_wrap():
    text = "as eireir tueroue asdiuodsi usaoifdu asdouusa doudas"
    wrapped = normalise(interactive.wrap(text, 20))
    assert wrapped == "as eireir tueroue\nasdiuodsi usaoifdu\nasdouusa doudas"


def test_comment():
    assert interactive.comment("a") == "# a"
    assert interactive.comment("a\nb") == "# a\n# b"
    assert interactive.comment("a\nb", indent_level=4) == "    # a\n    # b"
    assert interactive.comment("a\nb", comment_mark=";") == "; a\n; b"


def test_join_block():
    assert interactive.join_block("a", "", "") == "a"
    assert interactive.join_block("", "", "c") == "c"
    assert normalise(interactive.join_block("a", "", "c")) == "a\nc"
    assert normalise(interactive.join_block("", "b", "c")) == "b\nc"
    assert normalise(interactive.join_block("a", "b", "c")) == "a\nb\nc"


def test_long_option():
    for flags in (["-o", "--option"], ["--option", "-o"]):
        action = argparse.Action(flags, "dest")
        assert interactive.long_option(action).strip() == "--option"


def test_alternative_flags():
    for flags in (["-o", "--option", "-b"], ["--option", "-b", "-o"]):
        action = argparse.Action(flags, "dest")
        text = interactive.alternative_flags(action)
        assert "--option" not in text
        assert all([flag in text for flag in ("-o", "-b")])


def test_example_no_value():
    parser = ArgumentParser(conflict_handler="resolve")

    # When store_true option value is True, then it should not be commented
    action = parser.add_argument("--option", action="store_true")
    option_line = interactive.example_no_value(parser, action, {"option": True})
    assert option_line.strip() == "--option"
    option_line = interactive.example_no_value(parser, action, {"option": False})
    assert option_line.strip() == "# --option"

    # When store_false option value is False, then it should not be commented
    action = parser.add_argument("--option", action="store_false")
    option_line = interactive.example_no_value(parser, action, {"option": False})
    assert option_line.strip() == "--option"
    option_line = interactive.example_no_value(parser, action, {"option": True})
    assert option_line.strip() == "# --option"

    # When store_const option value is const, then it should not be commented
    action = parser.add_argument("--option", action="store_const", const=44, default=33)
    option_line = interactive.example_no_value(parser, action, {"option": 44})
    assert option_line.strip() == "--option"
    option_line = interactive.example_no_value(parser, action, {"option": 33})
    assert option_line.strip() == "# --option"

    # When no value is available in opts, then it should be commented
    action = argparse.Action(["--option", "-o"], "option", nargs=0)
    option_line = interactive.example_no_value(parser, action, {})
    assert option_line.strip() == "# --option"

    # When an extension is available, then it should not be commented
    option_line = interactive.example_no_value(
        parser, action, {"extensions": [Mock(flag="--option")]}
    )
    assert option_line.strip() == "--option"


def test_example_with_help():
    parser = ArgumentParser()
    action = parser.add_argument(
        "-o", "--option", action="store_true", help="do 42 things"
    )
    parser = ArgumentParser()
    text = """\
    # --option
        # (or alternatively: -o)
        # do 42 things
    """
    text = dedent(text)
    example = interactive.example_with_help(parser, action, {})
    assert normalise(dedent(text)) == normalise(example)

    # When option value is True, then it should not be commented
    text = """\
    --option
        # (or alternatively: -o)
        # do 42 things
    """
    example = interactive.example_with_help(parser, action, {"option": True})
    assert normalise(dedent(text)) == normalise(example)


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
    assert interactive.example(parser, action, {}).strip() == "# --option OPTION"
    assert interactive.example(parser, action, {"option": 32}).strip() == "--option 32"

    action = make_action(nargs=3)
    example = interactive.example(parser, action, {}).strip()
    assert example == "# --option OPTION OPTION OPTION"
    example = interactive.example(parser, action, {"option": [32, 21, 5]}).strip()
    assert example == "--option 32 21 5"

    action = make_action(nargs="*")
    example = interactive.example(parser, action, {}).strip()
    expected = ("# --option [OPTION [OPTION ...]]", "# --option [OPTION ...]")
    assert example in expected

    action = make_action(nargs="+")
    example = interactive.example(parser, action, {}).strip()
    assert example == "# --option OPTION [OPTION ...]"

    action = make_action(nargs="?")
    assert interactive.example(parser, action, {}).strip() == "# --option [OPTION]"

    # Positional argument:
    action = argparse.Action([], "arg", nargs=1, metavar="ARGUMENT")
    assert interactive.example(parser, action, {}).strip() == "# ARGUMENT"
    assert interactive.example(parser, action, {"arg": "value"}).strip() == "value"


def test_all_examples():
    parser = ArgumentParser()
    actions = [
        make_action(nargs=1),
        make_action(["--abc"], "abc", metavar="ABC", help="Abc-foobarize your project"),
    ]
    text = """\
    --option 23
        # (or alternatively: -o)
        # do 42 things


    # --abc ABC
        # Abc-foobarize your project
    """
    example = interactive.all_examples(parser, actions, {"option": 23})
    assert normalise(dedent(text)) == normalise(example)


def test_no_empty_example():
    # As reported on #333, the config flag was generating an empty example when the user
    # does not have a "{$XDG_CONFIG_HOME:-$HOME/.config}/pyscaffold/default.cfg" file,
    # which in turn generated the following error:
    #
    #    putup: error: argument --config: expected at least one argument
    #
    # This is a regression test to prevent that.

    # Explicit test case for the config example
    parser = ArgumentParser()
    extension = config.Config()
    extension.augment_cli(parser)
    action = next(a for a in parser._actions if "--config" in a.option_strings)
    example = interactive.example(parser, action, {"config_files": []})
    assert "# --config CONFIG_FILE" in normalise(example)  # example should be commented

    # Generalised test case
    parser = ArgumentParser()
    action = parser.add_argument("-x", dest="x", metavar="Y", nargs="+")
    example = interactive.example(parser, action, {"x": []})
    assert "# -x Y" in normalise(example)  # example should be commented
    example = interactive.example(parser, action, {"x": None})
    assert "# -x Y" in normalise(example)  # example should be commented


def test_multiple_options_same_dest():
    # General examples
    parser = ArgumentParser()
    x = parser.add_argument("-x", dest="val", action="store_const", const="x")
    y = parser.add_argument("-y", dest="val", action="store_const", const="y")

    # example should be commented when the value does not match
    example = normalise(interactive.example(parser, y, {"val": "x"}))
    assert "# -y" in example

    # example should be not commented when the value does match
    example = normalise(interactive.example(parser, y, {"val": "y"}))
    assert example.startswith("-y")

    # example should be commented when the value does not match
    example = normalise(interactive.example(parser, x, {"val": "y"}))
    assert "# -x" in example

    # example should be not commented when the value does match
    example = normalise(interactive.example(parser, x, {"val": "x"}))
    assert example.startswith("-x")

    # AD HOC examples found during debug
    # Just one of the 2 (`--config` or `--no-config`) should be activated in the example
    parser = ArgumentParser()
    extension = config.Config()
    extension.augment_cli(parser)

    nocfg = next(a for a in parser._actions if "--no-config" in a.option_strings)
    cfg = next(a for a in parser._actions if "--config" in a.option_strings)

    example = interactive.example(parser, nocfg, {"config_files": api.NO_CONFIG})
    assert normalise(example).startswith("--no-config")

    example = interactive.example(parser, cfg, {"config_files": api.NO_CONFIG})
    assert "# --config" in normalise(example)

    example = interactive.example(parser, cfg, {"config_files": ["file"]})
    assert normalise(example).startswith("--config file")

    example = interactive.example(parser, nocfg, {"config_files": ["file"]})
    assert "# --no-config" in normalise(example)


def test_commented_extension(monkeypatch):
    # When a flag is marked as commented
    config = {"comment": ["--option"], "ignore": []}
    monkeypatch.setattr(interactive, "get_config", lambda x: config[x])

    # And an extension corresponds to that flag
    parser = ArgumentParser()
    fake_extension = Mock(flag="--option")
    action = parser.add_argument(
        "--option", dest="extensions", action="append_const", const=fake_extension
    )
    option_line = interactive.example_no_value(
        parser, action, {"extensions": [fake_extension]}
    )
    # then it should be commented in the file
    assert option_line.strip() == "# --option"


def test_ignored_extension(monkeypatch):
    # When a flag is marked as ignored
    config = {"ignore": ["--option"], "comment": []}
    monkeypatch.setattr(interactive, "get_config", lambda x: config[x])

    # And an extension corresponds to that flag
    parser = ArgumentParser()
    fake_extension = Mock(flag="--option")
    action = parser.add_argument(
        "--option", dest="extensions", action="append_const", const=fake_extension
    )
    text = interactive.all_examples(parser, [action], {"extensions": [fake_extension]})
    # then it should be omitted
    assert "--option" not in text


def test_get_config():
    ignore = interactive.get_config("ignore")
    assert "--help" in ignore
    assert "--version" in ignore
    assert "--interactive" in ignore
    comment = interactive.get_config("comment")
    assert "--verbose" in comment
    assert "--very-verbose" in comment


def test_putup_real_examples():
    parser = ArgumentParser()
    cli.add_default_args(parser)
    for extension in cli.list_all_extensions():
        extension.augment_cli(parser)

    actions = interactive.get_actions(parser)
    text = normalise(interactive.all_examples(parser, actions, {}))
    assert "# --force" in text
    assert "# --update" in text
    assert "# --namespace" in text
    assert "# --no-tox" in text
    assert "--interactive" not in text
    assert "--help" not in text
    assert "--version" not in text


def test_cli(monkeypatch, tmpfolder):
    # When the user edit the contents of the file
    fake_content = """\
    myproj_path
    --name myproj
    --license gpl3
    --no-config
    # --namespace myns
    # ^  test commented options
    """
    fake_edit = tmpfolder / "pyscaffold.args"
    fake_edit.write_text(dedent(fake_content), "utf-8")
    monkeypatch.setattr("pyscaffold.shell.edit", lambda *_, **__: fake_edit)

    # Then, the options in the file should take place, not the ones given in the cli
    args = [
        "-vv",
        "--no-config",
        "--interactive",
        "myproj",
        "--no-tox",
        "--license",
        "mpl",
    ]
    cli.run(args)
    assert not (tmpfolder / "myproj").exists()
    assert (tmpfolder / "myproj_path/tox.ini").exists()
    assert (tmpfolder / "myproj_path/src/myproj/__init__.py").exists()
    license = (tmpfolder / "myproj_path/LICENSE.txt").read_text("utf-8")
    assert "GNU GENERAL PUBLIC LICENSE" in license
    assert "Version 3" in license
    # Commented options (or options that were not mentioned) should not take place
    assert not (tmpfolder / "myproj_path/src/myns").exists()
    assert not (tmpfolder / "myproj_path/.pre-commit-config.yaml").exists()
