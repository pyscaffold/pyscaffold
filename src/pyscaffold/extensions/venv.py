"""Create a virtual environment for the project"""
import argparse
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from ..file_system import chdir
from ..log import logger
from . import Extension, store_with

if TYPE_CHECKING:
    from ..actions import Action, ActionParams, ScaffoldOpts, Structure


DEFAULT = ".venv"


class Venv(Extension):
    """\
    Create a virtual environment for the project (using virtualenv or stdlib's venv).
    If ``virtualenv`` is available, it will be used, since it have some advantages over
    stdlib's ``venv`` (such as being faster, see https://virtualenv.pypa.io/en/stable/).

    Notice that even being part of Python's stdlib, ``venv`` is not guaranteed to be
    installed, some OS/distributions (such as Ubuntu) require an specific installation.
    """

    def augment_cli(self, parser: "argparse.ArgumentParser"):
        parser.add_argument(
            self.flag,
            action=store_with(self),
            nargs="?",
            const=DEFAULT,
            default=argparse.SUPPRESS,
            type=Path,
            help=self.help_text,
        )
        return self

    def activate(self, actions: List["Action"]) -> List["Action"]:
        return self.register(actions, run, before="report_done") + [instruct_user]


def run(struct: "Structure", opts: "ScaffoldOpts") -> "ActionParams":
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


def instruct_user(struct: "Structure", opts: "ScaffoldOpts") -> "ActionParams":
    """Simply display a message reminding the user to activate the venv."""

    with chdir(opts["project_path"]):
        venv_path = Path(opts.get("venv", DEFAULT))
        python_path = sorted(map(str, venv_path.glob("*/python*")), key=len)[0]
        pip_path = sorted(map(str, venv_path.glob("*/pip*")), key=len)[0]

    logger.warning(
        f"\nA virtual environment was created in the `{venv_path}` directory. "
        f"You need to activate it before using, or call directly {python_path} and "
        f"{pip_path}.\n"
    )

    return struct, opts


def create_with_virtualenv(path: Path, pretend=False):
    import virtualenv

    args = [str(path)]

    if pretend:
        virtualenv.session_via_cli(args)
    else:
        virtualenv.cli_run(args)

    logger.report("virtualenv", path)


def create_with_stdlib(path: Path, pretend=False):
    import venv

    if not pretend:
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
