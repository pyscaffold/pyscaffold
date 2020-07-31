"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: http://pre-commit.com
"""
from typing import List

from .. import shell, structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..exceptions import ShellCommandException
from ..file_system import chdir
from ..log import logger
from ..operations import no_overwrite
from ..templates import get_template
from . import Extension, venv

EXECUTABLE = "pre-commit"
CMD_OPT = "____command-pre_commit"  # we don't want this to be persisted


class PreCommit(Extension):
    """Generate pre-commit configuration file"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension

        Args:
            actions (list): list of actions to perform

        Returns:
            list: updated list of actions
        """
        actions = self.register(actions, add_files, after="define_structure")
        actions = self.register(actions, find_executable, after="define_structure")
        return self.register(actions, install, before="report_done")


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add .pre-commit-config.yaml file to structure

    Since the default template uses isort, this function also provides an
    initial version of .isort.cfg that can be extended by the user
    (it contains some useful skips, e.g. tox and venv)
    """
    files: Structure = {
        ".pre-commit-config.yaml": (get_template("pre-commit-config"), no_overwrite()),
        ".isort.cfg": (get_template("isort_cfg"), no_overwrite()),
    }

    return structure.merge(struct, files), opts


def find_executable(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Find the pre-commit exectuable that should run later in the next action...
    Or take advantage of the venv to install it...
    """
    pre_commit = shell.get_command(EXECUTABLE)
    opts = opts.copy()
    if pre_commit:
        opts.setdefault(CMD_OPT, pre_commit)
    else:
        # We can try to add it for venv to install... it will only work if the user is
        # already creating a venv anyway.
        opts.setdefault("venv_install", []).extend(["pre-commit"])

    return struct, opts


def install(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Attempts to install pre-commit in the project"""
    pre_commit = opts.get(CMD_OPT, shell.get_command(EXECUTABLE, venv.get_path(opts)))
    # ^  try again after venv, maybe it was installed
    msg = (
        "It is a good idea to update the hooks to the latest version:\n\n"
        "  pre-commit autoupdate\n\n"
        "Don't forget to tell your contributors to also install and use pre-commit.\n"
    )
    if pre_commit:
        try:
            with chdir(opts.get("project_path", ".")):
                pre_commit("install")
            logger.warning(f"\nA pre-commit hook was installed in your repo.\n{msg}")
            return struct, opts
        except ShellCommandException:
            logger.error(
                "\nImpossible to install pre-commit automatically, please open an "
                "issue in https://github.com/pyscaffold/pyscaffold/issues.\n",
                exc_info=True,
            )

    logger.warning(
        "\nA `.pre-commit-config.yaml` file was generated inside your project but in "
        "order to make sure the hooks will run, please install `pre-commit`:\n\n"
        f"  cd {opts['project_path']}\n"
        "  # it is a good idea to create and activate a virtualenv here\n"
        "  pip install pre-commit\n"
        f"  pre-commit install\n\n{msg}"
    )
    return struct, opts
