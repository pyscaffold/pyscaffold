import os
import shutil
import sys
from pathlib import Path

import virtualenv

from .system.helpers import normalize_run_args, run_with_debug

_DEFAULT_ENV = dict(os.environ)
_DEFAULT_ENV.pop("PYTHONPATH", None)  # ensure isolation
_PROJ_ROOT = str(Path(__file__).parent.parent)


class VirtualEnv:
    CREATE_OPTS = ["--no-setuptools", "--no-wheel"]

    def __init__(
        self,
        name: str,
        root: "os.PathLike[str]",
        opts=CREATE_OPTS,
        python=sys.executable,
        env=_DEFAULT_ENV,
    ):
        self.name = name
        self.root = Path(root)
        self.opts = opts
        self.path = self.root / name
        self.env = env
        self._python = python
        self._bin = self.path / ("Scripts" if os.name == "nt" else "bin")
        self._coverage_installed = False

    def create(self):
        args = [str(self.path), "--python", self._python, *self.opts]
        virtualenv.cli_run(args, env=self.env)

    def ensure_created(self):
        if not self.path.exists():
            self.create()

    def ensure_coverage(self):
        if self._coverage_installed:
            return

        return self.run(
            "pip install coverage --trusted-host pypi.python.org "
            "--trusted-host files.pythonhosted.org --trusted-host pypi.org"
        )
        self._coverage_installed = True

    def exe(self, cmd: str) -> str:
        return shutil.which(cmd, path=str(self._bin)) or shutil.which(cmd) or cmd

    def run(self, *args: str, with_coverage=False, **kwargs):
        self.ensure_created()
        args, kwargs = normalize_run_args(args, {"env": self.env, **kwargs})
        if with_coverage:
            self.ensure_coverage()
            coverage_dir = kwargs.pop("coverage_dir", ".")
            args = [
                *("coverage", "run", "--parallel-mode"),
                *("--rcfile", _coveragerc(coverage_dir)),
                *("--data-file", _coverage_data_file(coverage_dir)),
                *args,
            ]

        return run_with_debug([self.exe(args[0]), *args[1:]], kwargs)


def _coveragerc(coverage_dir) -> str:
    for root in (coverage_dir, os.getenv("TOXINIDIR", _PROJ_ROOT)):
        file = Path(root, ".coveragerc")  # change if configurations are moved
        if file.exists():
            return str(file)

    raise FileNotFoundError(file)


def _coverage_data_file(coverage_dir) -> str:
    for root in (coverage_dir, os.getenv("TOXINIDIR", _PROJ_ROOT)):
        path = Path(root)
        if list(path.glob(".coverage.*")) or (path / ".coverage").exists():
            return str(path / ".coverage")

    raise FileNotFoundError(".coverage (data_file to store coverage)")
