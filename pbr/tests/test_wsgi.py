# Copyright (c) 2015 Hewlett-Packard Development Company, L.P. (HP)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import re
import subprocess
import sys
import tempfile
import time
try:
    # python 2
    from urllib2 import urlopen
except ImportError:
    # python 3
    from urllib.request import urlopen

import fixtures

from pbr.tests import base


class TestWsgiScripts(base.BaseTestCase):

    cmd_names = ('pbr_test_wsgi', 'pbr_test_wsgi_with_class')

    def test_wsgi_script_install(self):
        """Test that we install a non-pkg-resources wsgi script."""
        if os.name == 'nt':
            self.skipTest('Windows support is passthrough')

        stdout, _, return_code = self.run_setup(
            'install', '--prefix=%s' % self.temp_dir)

        self.useFixture(
            fixtures.EnvironmentVariable(
                'PYTHONPATH', ".:%s/lib/python%s.%s/site-packages" % (
                    self.temp_dir,
                    sys.version_info[0],
                    sys.version_info[1])))

        self._check_wsgi_install_content(stdout)

    def test_wsgi_script_run(self):
        """Test that we install a runnable wsgi script.

        This test actually attempts to start and interact with the
        wsgi script in question to demonstrate that it's a working
        wsgi script using simple server. It's a bit hokey because of
        process management that has to be done.

        """
        self.skipTest("Test skipped until we can determine a reliable "
                      "way to capture subprocess stdout without blocking")

        if os.name == 'nt':
            self.skipTest('Windows support is passthrough')

        stdout, _, return_code = self.run_setup(
            'install', '--prefix=%s' % self.temp_dir)

        self.useFixture(
            fixtures.EnvironmentVariable(
                'PYTHONPATH', ".:%s/lib/python%s.%s/site-packages" % (
                    self.temp_dir,
                    sys.version_info[0],
                    sys.version_info[1])))
        # NOTE(sdague): making python unbuffered is critical to
        # getting output out of the subprocess.
        self.useFixture(
            fixtures.EnvironmentVariable(
                'PYTHONUNBUFFERED', '1'))

        self._check_wsgi_install_content(stdout)

        # Live test run the scripts and see that they respond to wsgi
        # requests.
        self._test_wsgi()

    def _test_wsgi(self):
        for cmd_name in self.cmd_names:
            cmd = os.path.join(self.temp_dir, 'bin', cmd_name)
            stdout = tempfile.NamedTemporaryFile()
            print("Running %s > %s" % (cmd, stdout.name))
            # NOTE(sdague): ok, this looks a little janky, and it
            # is. However getting python to not hang with
            # popen.communicate is beyond me.
            #
            # We're opening with a random port (so no conflicts), and
            # redirecting all stdout and stderr to files. We can then
            # safely read these files and not deadlock later in the
            # test. This requires shell expansion.
            p = subprocess.Popen(
                "%s -p 0 > %s 2>&1" % (cmd, stdout.name),
                shell=True,
                close_fds=True,
                cwd=self.temp_dir)

            self.addCleanup(p.kill)

            # the sleep is important to force a context switch to the
            # subprocess
            time.sleep(0.1)

            stdoutdata = stdout.read()
            self.assertIn(
                "STARTING test server pbr_testpackage.wsgi",
                stdoutdata)
            self.assertIn(
                "DANGER! For testing only, do not use in production",
                stdoutdata)

            m = re.search('(http://[^:]+:\d+)/', stdoutdata)
            self.assertIsNotNone(m, "Regex failed to match on %s" % stdoutdata)

            f = urlopen(m.group(1))
            self.assertEqual("Hello World", f.read())

            # the sleep is important to force a context switch to the
            # subprocess
            time.sleep(0.1)

            # Kill off the child, it should force a flush of the stdout.
            p.kill()
            time.sleep(0.1)

            stdoutdata = stdout.read()
            # we should have logged an HTTP request, return code 200, that
            # returned 11 bytes
            self.assertIn('"GET / HTTP/1.1" 200 11', stdoutdata)

    def _check_wsgi_install_content(self, install_stdout):
        for cmd_name in self.cmd_names:
            install_txt = 'Installing %s script to %s' % (cmd_name,
                                                          self.temp_dir)
            self.assertIn(install_txt, install_stdout)

            cmd_filename = os.path.join(self.temp_dir, 'bin', cmd_name)

            script_txt = open(cmd_filename, 'r').read()
            self.assertNotIn('pkg_resources', script_txt)

            main_block = """if __name__ == "__main__":
    import argparse
    import socket
    import wsgiref.simple_server as wss"""

            if cmd_name == 'pbr_test_wsgi':
                app_name = "main"
            else:
                app_name = "WSGI.app"

            starting_block = ("STARTING test server pbr_testpackage.wsgi."
                              "%s" % app_name)

            else_block = """else:
    application = None"""

            self.assertIn(main_block, script_txt)
            self.assertIn(starting_block, script_txt)
            self.assertIn(else_block, script_txt)
