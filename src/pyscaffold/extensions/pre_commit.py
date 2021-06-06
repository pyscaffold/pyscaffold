"""
Extension that generates configuration files for Yelp `pre-commit`_.

.. _pre-commit: https://pre-commit.com
"""
from functools import partial
from typing import List

from .. import shell, structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from ..exceptions import ShellCommandException
from ..file_system import chdir
from ..log import logger
from ..operations import FileOp, no_overwrite
from ..structure import AbstractContent, ResolvedLeaf
from ..templates import get_template
from . import Extension, venv

EXECUTABLE = "pre-commit"
CMD_OPT = "____command-pre_commit"  # we don't want this to be persisted
INSERT_AFTER = ".. _pyscaffold-notes:\n"

UPDATE_MSG = """
It is a good idea to update the hooks to the latest version:

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.
"""

SUCCESS_MSG = "\nA pre-commit hook was installed in your repo." + UPDATE_MSG

ERROR_MSG = """
Impossible to install pre-commit automatically, please open an issue in
https://github.com/pyscaffold/pyscaffold/issues.
"""

INSTALL_MSG = f"""
A `.pre-commit-config.yaml` file was generated inside your project but in
order to make sure the hooks will run, please install `pre-commit`:

    cd {{project_path}}
    # it is a good idea to create and activate a virtualenv here
    pip install pre-commit
{UPDATE_MSG}
"""

README_NOTE = f"""
Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
changes::

    pip install pre-commit
    cd {{name}}
    pre-commit install
{UPDATE_MSG.replace(':', '::')}
.. _pre-commit: https://pre-commit.com/
"""


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

    struct = structure.modify(struct, "README.rst", partial(add_instructions, opts))
    return structure.merge(struct, files), opts


def find_executable(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Find the pre-commit executable that should run later in the next action...
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
    project_path = opts.get("project_path", "PROJECT_DIR")
    pre_commit = opts.get(CMD_OPT) or shell.get_command(EXECUTABLE, venv.get_path(opts))
    # ^  try again after venv, maybe it was installed
    if pre_commit:
        try:
            with chdir(opts.get("project_path", "."), **opts):
                pre_commit("install", log=True, pretend=opts.get("pretend"))
            logger.warning(SUCCESS_MSG)
            return struct, opts
        except ShellCommandException:
            logger.error(ERROR_MSG, exc_info=True)

    logger.warning(INSTALL_MSG.format(project_path=project_path))
    return struct, opts


def add_instructions(
    opts: ScaffoldOpts, content: AbstractContent, file_op: FileOp
) -> ResolvedLeaf:
    """Add pre-commit instructions to README"""
    text = structure.reify_content(content, opts)
    if text is not None:
        i = text.find(INSERT_AFTER)
        assert i > 0, f"{INSERT_AFTER!r} not found in README template:\n{text}"
        j = i + len(INSERT_AFTER)
        text = text[:j] + README_NOTE.format(**opts) + text[j:]
    return text, file_op
