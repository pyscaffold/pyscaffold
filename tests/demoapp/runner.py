"""Runner module for demoapp"""

import argparse
import sys

import demoapp


def parse_args(args):
    """Parse command line parameters

    Args:
        args: command line parameters as list of strings

    Returns:
        :obj:`argparse.Namespace`: command line parameters
    """
    parser = argparse.ArgumentParser(
        description="A demo application for PyScaffold's unit testing"
    )
    version = demoapp.__version__
    parser.add_argument(
        "-v", "--version", action="version", version=f"demoapp {version}"
    )
    opts = parser.parse_args(args)
    return opts


def main(args):
    parse_args(args)
    print("Hello World")


def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
