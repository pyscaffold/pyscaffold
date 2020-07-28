import argparse

from pyscaffold import extensions

from .extensions.helpers import make_extension


def test_extension():
    parser = argparse.ArgumentParser()
    extension = make_extension("MyExtension")
    extension.augment_cli(parser)
    opts = vars(parser.parse_args(["--my-extension"]))
    assert opts["extensions"] == [extension]


def test_extension_append():
    parser = argparse.ArgumentParser()
    extension1 = make_extension("MyExtension1")
    extension2 = make_extension("MyExtension2")
    parser.set_defaults(extensions=[extension1])

    extension2.augment_cli(parser)
    opts = vars(parser.parse_args(["--my-extension2"]))
    assert opts["extensions"] == [extension1, extension2]


def test_include():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", nargs=0, action=extensions.include(*my_extensions))
    opts = vars(parser.parse_args(["--opt"]))
    assert opts["extensions"] == my_extensions


def test_store_with():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", action=extensions.store_with(*my_extensions))
    opts = vars(parser.parse_args(["--opt", "42"]))
    assert opts["extensions"] == my_extensions
    assert opts["opt"] == "42"


def test_store_with_type():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", type=int, action=extensions.store_with(*my_extensions))
    opts = vars(parser.parse_args(["--opt", "42"]))
    assert opts["extensions"] == my_extensions
    assert opts["opt"] == 42
