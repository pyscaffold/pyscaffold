#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for our unittest demo application
"""

import sys
from setuptools import setup

# Add here console scripts and other entry points in ini-style format
entry_points = """
[console_scripts]
demoapp_data = demoapp_data.runner:run
"""


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup(setup_requires=['pyscaffold>=3.0a0,<3.1a0'] + sphinx,
          entry_points=entry_points,
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
