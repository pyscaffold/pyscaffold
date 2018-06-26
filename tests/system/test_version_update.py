# -*- coding: utf-8 -*-
from inspect import currentframe, getfile
from os import environ, getcwd
from os.path import dirname
from os.path import join as path_join
from os.path import normpath
from shutil import copy

import pytest

from .helpers import run, run_common_tasks

pytestmark = [pytest.mark.slow, pytest.mark.system]

LOCATION = path_join(getcwd(), dirname(getfile(currentframe())))

TESTS_MISC = normpath(path_join(LOCATION, '..', 'misc'))


# TODO: Check if we need the following test (and if we need it, make it
# actually run, since python 2.7 tests are disabled in travis)
@pytest.mark.skipif(environ.get('DISTRIB') != 'conda' or
                    environ.get('PYTHON_VERSION') != '2.7',
                    reason='should only be executed with version 2.7 in conda')
def test_update_from_v20(tmpdir):
    with tmpdir.as_cwd():
        run('git clone --branch v0.2.1 '
            'https://github.com/blue-yonder/pydse.git pydse')
        copy(path_join(TESTS_MISC, 'pydse_setup.cfg'), 'pydse/setup.cfg')
        run('putup --update pydse')
        run('conda install --yes nomkl numpy scipy matplotlib libgfortran')
        run('pip install -v -r pydse/requirements.txt')
        run_common_tasks()
