"""Runner module for demoapp_data"""

import argparse
import os
import sys
from difflib import unified_diff
from pkgutil import get_data

if sys.version_info[:2] >= (3, 7):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.7`
    from importlib.resources import read_text
else:
    from importlib_resources import read_text

from . import __name__ as pkg_name
from . import __version__ as pkg_version
from . import data as data_pkg


def get_hello_world_pkgutil():
    return get_data(pkg_name, os.path.join("data", "hello_world.txt")).decode().strip()


def get_hello_world_importlib():
    return read_text(data_pkg.__name__, "hello_world.txt").strip()


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="A demo application for PyScaffold's unit testing"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"demoapp_data {pkg_version}"
    )
    opts = parser.parse_args(args)
    return opts


def main(args):
    parse_args(args)
    # check several ways of reading in data
    data_pkgutil = get_hello_world_pkgutil()
    data_importlib = get_hello_world_importlib()
    diff = unified_diff(
        (data_pkgutil + "\n").splitlines(keepends=True),
        (data_importlib + "\n").splitlines(keepends=True),
        fromfile="pkgutil_data",
        tofile="importlib_data",
    )
    print(data_pkgutil + "\n-------------------------------------\n")
    msg = f"data obtained via pkgutil and importlib differ:\n\n{''.join(diff)}\n"
    print(f"data_pkgutil = {type(data_pkgutil).__name__}({data_pkgutil!r})")
    print(f"data_importlib = {type(data_importlib).__name__}({data_importlib!r})\n")
    assert data_pkgutil == data_importlib, msg


def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
