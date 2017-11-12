# -*- coding: utf-8 -*-

"""
This module provides a test runner for setup.py copied over from
https://bitbucket.org/pytest-dev/pytest-runner/
in order to make some improvements.

This file is MIT licensed:

Copyright (c) 2011 Jason R. Coombs <jaraco@jaraco.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import division, print_function, absolute_import

import sys
import os
import shlex

import pkg_resources
from setuptools.command.test import test as TestCommand

__author__ = "Jason R. Coombs, Florian Wilhelm"
__copyright__ = "Jason R. Coombs"
__license__ = "MIT"


class PyTest(TestCommand):
    user_options = [
        ('extras', None, "Install (all) setuptools extras when running tests"),
        ('index-url=', None, "Specify an index url from which to retrieve "
            "dependencies"),
        ('allow-hosts=', None, "Whitelist of comma-separated hosts to allow "
            "when retrieving dependencies"),
        ('addopts=', 'a', "Additional options to be passed verbatim to the "
            "pytest runner")
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.extras = False
        self.index_url = None
        self.allow_hosts = None
        self.addopts = []

    def finalize_options(self):
        if self.addopts:
            self.addopts = shlex.split(self.addopts)

    @staticmethod
    def marker_passes(marker):
        """
        Given an environment marker, return True if the marker is valid
        and matches this environment.
        """
        return (
            marker
            and not pkg_resources.invalid_marker(marker)
            and pkg_resources.evaluate_marker(marker)
        )

    def run(self):
        """
        Override run to ensure requirements are available in this session (but
        don't install them anywhere).
        """
        self._build_egg_fetcher()
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)
        extras_require = self.distribution.extras_require or {}
        for spec, reqs in extras_require.items():
            name, sep, marker = spec.partition(':')
            if marker and not self.marker_passes(marker):
                continue
            # always include unnamed extras
            if not name or self.extras:
                self.distribution.fetch_build_eggs(reqs)
        if self.dry_run:
            self.announce('skipping tests (dry run)')
            return
        self.with_project_on_sys_path(self.run_tests)
        if self.result_code:
            raise SystemExit(self.result_code)
        return self.result_code

    def _build_egg_fetcher(self):
        """Build an egg fetcher that respects index_url and allow_hosts"""
        # modified from setuptools.dist:Distribution.fetch_build_egg
        from setuptools.command.easy_install import easy_install
        main_dist = self.distribution
        # construct a fake distribution to store the args for easy_install
        dist = main_dist.__class__({'script_args': ['easy_install']})
        dist.parse_config_files()
        opts = dist.get_option_dict('easy_install')
        keep = (
            'find_links', 'site_dirs', 'index_url', 'optimize',
            'site_dirs', 'allow_hosts'
        )
        for key in opts.keys():
            if key not in keep:
                del opts[key]   # don't use any other settings
        if main_dist.dependency_links:
            links = main_dist.dependency_links[:]
            if 'find_links' in opts:
                links = opts['find_links'][1].split() + links
            opts['find_links'] = ('setup', links)
        if self.allow_hosts:
            opts['allow_hosts'] = ('test', self.allow_hosts)
        if self.index_url:
            opts['index_url'] = ('test', self.index_url)
        install_dir_func = getattr(dist, 'get_egg_cache_dir', os.getcwd)
        install_dir = install_dir_func()
        cmd = easy_install(
            dist, args=["x"], install_dir=install_dir, exclude_scripts=True,
            always_copy=False, build_directory=None, editable=False,
            upgrade=False, multi_version=True, no_report=True
        )
        cmd.ensure_finalized()
        main_dist._egg_fetcher = cmd

    def run_tests(self):
        try:
            import pytest
        except ImportError:
            raise RuntimeError("PyTest is not installed, run: "
                               "pip install pytest pytest-cov")
        errno = pytest.main(self.addopts)
        sys.exit(errno)
