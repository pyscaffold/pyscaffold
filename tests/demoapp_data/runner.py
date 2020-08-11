"""Runner module for demoapp_data"""

import argparse
import os
import sys
from pkgutil import get_data

if sys.version_info[:2] >= (3, 7):
    from importlib.resources import read_text
else:
    from importlib_resources import read_text

from . import __name__ as pkg_name
from . import __version__ as pkg_version
from . import data as data_pkg


def get_hello_world_pkgutil():
    data = get_data(pkg_name, os.path.join("data", "hello_world.txt"))
    return data.decode()


def get_hello_world_importlib():
    return read_text(data_pkg.__name__, "hello_world.txt")


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
    hello_world_pkgutil = get_hello_world_pkgutil()
    hello_world_importlib = get_hello_world_importlib()
    assert hello_world_pkgutil == hello_world_importlib
    print(hello_world_pkgutil)


def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
