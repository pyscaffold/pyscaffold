# -*- coding: utf-8 -*-

"""Runner module for demoapp_data"""

from __future__ import absolute_import, division, print_function

import argparse
import os
import sys
from pkgutil import get_data

import demoapp_data

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def get_hello_world():
    pkg_name = __name__.split('.', 1)[0]
    data = get_data(pkg_name, os.path.join('data', 'hello_world.txt'))
    if sys.version_info[0] >= 3:
        data = data.decode()
    return data


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="A demo application for PyScaffold's unit testing")
    version = demoapp_data.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='demoapp_data {ver}'.format(ver=version))
    opts = parser.parse_args(args)
    return opts


def main(args):
    parse_args(args)
    hello_world = get_hello_world()
    print(hello_world)


def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
