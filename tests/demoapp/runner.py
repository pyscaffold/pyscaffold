# -*- coding: utf-8 -*-

"""Runner module for demoapp"""

from __future__ import absolute_import, division, print_function

import argparse
import sys

import demoapp

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="A demo application for PyScaffold's unit testing")
    version = demoapp.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='demoapp {ver}'.format(ver=version))
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


if __name__ == '__main__':
    main(sys.argv[1:])
