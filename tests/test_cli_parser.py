import argparse

from pyscaffold.cli_parser import ArgumentParser, is_included, merge_user_input
from pyscaffold.extensions import include, store_with
from pyscaffold.extensions.cirrus import Cirrus
from pyscaffold.extensions.travis import Travis


def test_is_included():
    extensions = [Cirrus(), Travis()]
    cirrus_fake_action = argparse.Action(["--cirrus"], "option", nargs=0)
    namespace_fake_action = argparse.Action(["--namespace"], "option", nargs=0)

    assert is_included(cirrus_fake_action, extensions)
    assert not is_included(namespace_fake_action, extensions)


def test_merge_user_input_flag():
    existing_opts = {"name": "proj"}

    parser = ArgumentParser()
    action = parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        required=False,
    )

    merged = merge_user_input(parser, existing_opts, True, action)
    assert merged == {"name": "proj", "force": True}

    merged = merge_user_input(parser, existing_opts, False, action)
    assert merged == {"name": "proj", "force": False}


def test_merge_user_input_choices():
    existing_opts = {"name": "proj"}

    parser = ArgumentParser()
    license_choices = ["mit", "gpl"]

    def _best_fit_license(_):
        return "gpl"

    action = parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        type=_best_fit_license,
        required=False,
        metavar="LICENSE",
    )

    # Coercion with type should work
    merged = merge_user_input(parser, existing_opts, "mit", action)
    assert merged == {"name": "proj", "license": "gpl"}


def test_merge_user_input_list():
    existing_opts = {"name": "proj"}

    parser = ArgumentParser()
    action = parser.add_argument(
        "-x", "--X", dest="x", type=int, choices=range(10), nargs="+"
    )

    merged = merge_user_input(parser, existing_opts, [1, 2], action)
    assert merged == {"name": "proj", "x": [1, 2]}

    action = parser.add_argument(
        "-y", "--Y", dest="y", type=int, choices=range(10), nargs="*"
    )

    merged = merge_user_input(parser, existing_opts, [], action)
    assert merged == {"name": "proj", "y": []}


def test_merge_user_input_include():
    existing_opts = {"name": "proj"}

    included_extensions = [Cirrus(), Travis()]
    parser = ArgumentParser()
    action = parser.add_argument(
        "-x",
        "--X",
        action=include(*included_extensions),
        required=False,
    )

    merged = merge_user_input(parser, existing_opts, True, action)
    assert merged == {"name": "proj", "extensions": included_extensions}


def test_merge_user_input_store_with():
    existing_opts = {"name": "proj"}

    included_extensions = [Cirrus(), Travis()]
    parser = ArgumentParser()
    action = parser.add_argument(
        "-x",
        "--X",
        dest="x",
        action=store_with(*included_extensions),
        required=False,
    )

    merged = merge_user_input(parser, existing_opts, "value", action)
    assert merged == {"name": "proj", "extensions": included_extensions, "x": "value"}
