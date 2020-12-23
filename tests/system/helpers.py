# -*- coding: utf-8 -*-
import os
import shlex
import sys
import traceback
from os import environ
from subprocess import STDOUT, CalledProcessError, check_output

IS_POSIX = os.name == "posix"
PYTHON = sys.executable
"""Same python executable executing the tests... Hopefully the one inside the virtualenv
inside tox folder. If we install packages by mistake is not a huge problem.
"""


def run(*args, **kwargs):
    """Run the external command. See ``subprocess.check_output``."""
    # normalize args
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0], posix=IS_POSIX)
        else:
            args = args[0]

    # if args[0] in ("python", "putup", "pip", "tox", "pytest", "pre-commit"):
    #     raise SystemError("Please specify an executable with explicit path")

    opts = dict(stderr=STDOUT, universal_newlines=True)
    opts.update(kwargs)

    try:
        return check_output(args, **opts)
    except CalledProcessError as ex:
        print("Error while running command:")
        print(args)
        print(opts)
        traceback.print_exc()
        msg = "******************** Terminal ($? = {}) ********************\n{}"
        print(msg.format(ex.returncode, ex.output))
        raise


def merge_env(other=None, **kwargs):
    """Create a dict from merging items to the current ``os.environ``"""
    env = {k: v for k, v in environ.items()}  # Clone the environ as a dict
    env.update(other or {})
    env.update(kwargs)
    return env


def run_common_tasks(tests=True, flake8=True):
    if tests:
        run("{PYTHON} -m pytest".format(PYTHON=PYTHON), env=merge_env(PYTHONPATH="src"))

    run("{PYTHON} setup.py doctest".format(PYTHON=PYTHON))
    run("{PYTHON} setup.py docs".format(PYTHON=PYTHON))
    run("{PYTHON} setup.py --version".format(PYTHON=PYTHON))
    run("{PYTHON} setup.py sdist".format(PYTHON=PYTHON))
    run("{PYTHON} setup.py bdist".format(PYTHON=PYTHON))

    if flake8 and environ.get("COVERAGE") == "true":
        run("flake8 --count")
