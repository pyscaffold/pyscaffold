import logging
import os
import shlex
import sys
import traceback
from importlib.util import find_spec
from os import environ
from pathlib import Path
from shutil import which
from subprocess import STDOUT, CalledProcessError, check_output

import pytest

IS_POSIX = os.name == "posix"

PYTHON = sys.executable
"""Same python executable executing the tests... Hopefully the one inside the virtualenv
inside tox folder. If we install packages by mistake is not a huge problem.
"""


def find_package_bin(package, binary=None):
    """If a ``package`` can be executed via ``python -m`` (with the current python)
    try to do that, otherwise use ``binary`` on the $PATH"""
    binary = binary or package
    if find_spec(package):
        return f"{PYTHON} -m {package}"

    executable = which(binary)
    if executable:
        msg = "Package %s can not be found inside %s, using system executable %s"
        logging.critical(msg, package, sys.prefix, executable)
        return executable

    pytest.skip(f"For some reason {binary} cannot be found.")


def find_venv_bin(venv_path, bin_name):
    """Given the path for a venv, find a executable there"""
    assert Path(venv_path).exists()
    candidates = list(map(str, Path(venv_path).glob(f"*/{bin_name}*")))
    return sorted(candidates, key=len)[0]


def merge_env(other=None, **kwargs):
    """Create a dict from merging items to the current ``os.environ``"""
    env = {k: v for k, v in environ.items()}  # Clone the environ as a dict
    env.update(other or {})
    env.update(kwargs)
    return env


def run(*args, **kwargs):
    """Run the external command. See ``subprocess.check_output``."""
    # normalize args
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0], posix=IS_POSIX)
        else:
            args = args[0]

    if args[0] in ("python", "putup", "pip", "tox", "pytest", "pre-commit"):
        raise SystemError("Please specify an executable with explicit path")

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


def sphinx_cmd(build):
    docs_dir = Path("docs")
    build_dir = docs_dir / "_build"
    doctrees = build_dir / "doctrees"
    output_dir = build_dir / build
    return f"{PYTHON} -m sphinx -b {build} -d {doctrees} {docs_dir} {output_dir}"


def run_common_tasks(tests=True, flake8=True):
    if tests:
        run(f"{PYTHON} -m pytest", env=merge_env(PYTHONPATH="src"))

    run(sphinx_cmd("doctest"))
    run(sphinx_cmd("html"))

    run(f"{PYTHON} setup.py --version")
    run(f"{PYTHON} setup.py sdist")
    run(f"{PYTHON} setup.py bdist")
    run(f"{PYTHON} -m build .")

    if flake8 and environ.get("COVERAGE") == "true":
        run(f"{PYTHON} -m flake8 --count")
