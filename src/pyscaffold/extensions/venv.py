"""Create a virtual environment for the project"""
import argparse
import os
from contextlib import suppress
from pathlib import Path
from typing import List, Optional

from .. import dependencies as deps
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..file_system import chdir
from ..identification import get_id
from ..log import logger
from ..shell import get_command, get_executable
from . import Extension, store_with

DEFAULT: os.PathLike = Path(".venv")


class Venv(Extension):
    """\
    Create a virtual environment for the project (using virtualenv or stdlib's venv).
    Default location: "{DEFAULT}".

    If ``virtualenv`` is available, it will be used, since it have some advantages over
    stdlib's ``venv`` (such as being faster, see https://virtualenv.pypa.io/en/stable/).

    Notice that even if part of Python's stdlib, ``venv`` is not guaranteed to be
    installed, some OS/distributions (such as Ubuntu) require an explicit installation.
    If you have problems, try installing virtualenv with pip and run the command again.
    """

    persist = False  # We just want the virtual env to be created on fresh projects

    def augment_cli(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            self.flag,
            action=store_with(self),
            nargs="?",
            const=DEFAULT,
            default=argparse.SUPPRESS,
            type=Path,
            help=self.help_text.format(DEFAULT=DEFAULT),
        )
        parser.add_argument(
            "--venv-install",
            action=store_with(self),
            nargs="+",
            default=argparse.SUPPRESS,
            metavar="PACKAGE",
            help="install packages inside the created venv. "
            "The packages can have dependency ranges as if they would be written to a "
            "`requirements.txt` file, but remember to use quotes to avoid messing with "
            "the terminal",
        )
        return self

    def activate(self, actions: List[Action]) -> List[Action]:
        actions = self.register(actions, run, after="create_structure")
        actions = self.register(actions, install_packages, after=get_id(run))
        return self.register(actions, instruct_user, before="report_done")


def run(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Action that will create a virtualenv for the project"""

    project_path = opts["project_path"]
    venv_path = Path(opts.get("venv", DEFAULT))

    with chdir(project_path):
        if venv_path.is_dir():
            logger.report("skip", venv_path)
            return struct, opts

        for creator in (create_with_virtualenv, create_with_stdlib):
            with suppress(ImportError):
                creator(venv_path, opts.get("pretend"))
                break
        else:
            # no break statement found, so no creator function executed correctly
            raise NotInstalled()

    return struct, opts


def install_packages(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Install the specified packages inside the created venv."""

    packages = opts.get("venv_install")
    if not packages:
        return struct, opts

    pretend = opts.get("pretend")
    venv_path = get_path(opts)

    if not pretend:
        pip = get_command("pip", venv_path, include_path=False)
        if not pip:
            raise NotInstalled(f"pip cannot be found inside {venv_path}")
        pip("install", "-U", *deps.deduplicate(packages))

    logger.report("pip", f"install -U {' '.join(packages)} [{venv_path}]")
    return struct, opts


def instruct_user(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Simply display a message reminding the user to activate the venv."""

    with chdir(opts["project_path"]):
        venv_path = Path(opts.get("venv", DEFAULT))
        python = get_executable("python", venv_path, include_path=False)
        pip = get_executable("pip", venv_path, include_path=False)

    logger.warning(
        f"\nA virtual environment was created in the `{venv_path}` directory. "
        f"You need to activate it before using, or call directly {python} and {pip}.\n"
    )

    return struct, opts


def get_path(opts: ScaffoldOpts, default=DEFAULT) -> Path:
    """Get the path to the venv that will be created."""
    with chdir(opts.get("project_path", ".")):
        return Path(opts.get("venv", default)).resolve()


def create_with_virtualenv(path: Path, pretend=False):
    import virtualenv

    args = [str(path)]

    if pretend:
        virtualenv.session_via_cli(args)
    else:
        logger.warning("\nInstalling virtual environment, it might take a while...\n")
        virtualenv.cli_run(args)

    logger.report("virtualenv", path)


def create_with_stdlib(path: Path, pretend=False):
    import venv

    if not pretend:
        logger.warning("\nInstalling virtual environment, it might take a while...\n")
        venv.create(str(path), with_pip=True)

    logger.report("venv", path)


class NotInstalled(ImportError):
    """Neither virtualenv or venv are installed in the computer. Please check the
    following alternatives:

    - ``virtualenv`` can be installed via pip
    - ``venv`` is supposed to installed by default with Python3, however some OS or
      distributions (such as Ubuntu) break the standard library in a series of packages
      that need to be manually installed via OS package manager.
      You can try to search for a ``python-venv``, ``python3-venv`` or similar in the
      official repositories.
    """

    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or self.__doc__)
