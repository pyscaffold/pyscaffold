"""Runner module for demoapp_data"""

import argparse
import os
import sys
from pkgutil import get_data

if sys.version_info[:2] >= (3, 7):
    from importlib.resources import read_text
else:
    from importlib_resources import read_text

import demoapp_data


def get_hello_world_pkgutil():
    pkg_name = __name__.split(".", 1)[0]
    data = get_data(pkg_name, os.path.join("data", "hello_world.txt"))
    return data.decode()


def get_hello_world_importlib():
    return read_text(__name__ + ".data", "hello_world.txt")


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="A demo application for PyScaffold's unit testing"
    )
    version = demoapp_data.__version__
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="demoapp_data {ver}".format(ver=version),
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
