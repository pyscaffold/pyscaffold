"""
External API for accessing PyScaffold programmatically via Python.
"""
from enum import Enum
from functools import reduce
from pathlib import Path

import pyscaffold

from . import actions, info
from .exceptions import NoPyScaffoldProject

# -------- Options --------

(NO_CONFIG,) = list(Enum("ConfigFiles", "NO_CONFIG"))  # type: ignore
"""This constant is used to tell PyScaffold to not load any extra configuration file,
not even the default ones
Usage::

    create_project(opts, config_files=NO_CONFIG)

Please notice that the ``setup.cfg`` file inside an project being updated will
still be considered.
"""

DEFAULT_OPTIONS = {
    "update": False,
    "force": False,
    "description": "Add a short description here!",
    "url": "https://github.com/pyscaffold/pyscaffold/",
    "license": "mit",
    "version": pyscaffold.__version__,
    "classifiers": ["Development Status :: 4 - Beta", "Programming Language :: Python"],
    "extensions": [],
    "config_files": [],  # Overloaded in bootstrap_options for lazy evaluation
}


def bootstrap_options(opts=None, **kwargs):
    """Internal API: augment the given options with minimal defaults
    and existing configurations saved in files (e.g. ``setup.cfg``)

    See list of arguments in :obj:`create_project`.
    Returns a dictionary of options.

    Warning:
        This function is not part of the public Python API of PyScaffold, and therefore
        might change even in minor/patch releases (not bounded to semantic versioning).

    Note:
        This function does not replace the :obj:`pyscaffold.actions.get_default_options`
        action. Instead it is needed to ensure that action works correctly.
    """
    opts = opts.copy() if opts else {}
    opts.update(kwargs)

    # Clean up:
    opts = {k: v for k, v in opts.items() if v or v is False}
    # ^  remove empty items, so we ensure setdefault works

    # Add options stored in config files:
    default_files = [info.config_file(default=None)]
    opts.setdefault("config_files", [f for f in default_files if f and f.exists()])
    # ^  make sure the file exists before passing it ahead
    opts = _read_existing_config(opts)

    # Add defaults last, so they don't overwrite:
    opts.update({k: v for k, v in DEFAULT_OPTIONS.items() if k not in opts})

    return opts


# -------- Public API --------


def create_project(opts=None, **kwargs):
    """Create the project's directory structure

    Args:
        opts (dict): options of the project
        **kwargs: extra options, passed as keyword arguments

    Returns:
        tuple: a tuple of `struct` and `opts` dictionary

    Valid options include:

    :Project Information:   - **project_path** (:class:`os.PathLike`)

    :Naming:                - **name** (*str*)
                            - **package** (*str*)

    :Package Information:   - **author** (*str*)
                            - **email** (*str*)
                            - **release_date** (*str*)
                            - **year** (*str*)
                            - **title** (*str*)
                            - **description** (*str*)
                            - **url** (*str*)
                            - **classifiers** (*str*)
                            - **requirements** (*list*)

    :PyScaffold Control:    - **update** (*bool*)
                            - **force** (*bool*)
                            - **pretend** (*bool*)
                            - **extensions** (*list*)
                            - **config_files** (*list* | ``NO_CONFIG``)

    Some of these options are equivalent to the command line options, others
    are used for creating the basic python package meta information, but the
    last tree can change the way PyScaffold behaves.

    When the **force** flag is ``True``, existing files will be overwritten.
    When the **update** flag is ``True``, PyScaffold will consider that some
    files can be updated (usually the packaging boilerplate),
    but will keep others intact.
    When the **pretend** flag is ``True``, the project will not be
    created/updated, but the expected outcome will be logged.

    The **extensions** list may contain any object that follows the
    `extension API <../extensions>`_. Note that some PyScaffold features, such
    as travis, tox and pre-commit support, are implemented as built-in
    extensions. In order to use these features it is necessary to include the
    respective objects in the extension list. All built-in extensions are
    accessible via :mod:`pyscaffold.extensions` submodule.

    Finally, when ``setup.cfg``-like files are added to the **config_files** list,
    PyScaffold will read it's options from there in addition to the ones already passed.
    If the list is empty, the default configuration file is used. To avoid reading any
    existing configuration, please pass ``config_file=NO_CONFIG``.
    See https://pyscaffold.org/en/latest/configuration.html for more details.

    Note that extensions may define extra options. For example, the
    cookiecutter extension define a ``cookiecutter`` option that
    should be the address to the git repository used as template.
    """
    opts = bootstrap_options(opts, **kwargs)
    pipeline = actions.discover(opts["extensions"])

    # call the actions to generate final struct and opts
    struct, opts = reduce(lambda acc, f: actions.invoke(f, *acc), pipeline, ({}, opts))
    return struct, opts


# -------- Auxiliary functions (Private) --------


def _read_existing_config(opts):
    """Read existing config files first listed in ``opts["config_files"]``
    and then ``setup.cfg`` inside ``opts["project_path"]``
    """
    config_files = opts["config_files"]
    if config_files is not NO_CONFIG:
        paths = (Path(f).resolve() for f in config_files)
        deduplicated = {p: p for p in paths}
        # ^  using a dict instead of a set to preserve the order the files were given
        # ^  we do not mute errors here if the file does not exist. Let us be
        #    explicit.
        opts = reduce(lambda acc, f: info.project(acc, f), deduplicated.keys(), opts)

    if opts.get("update"):
        try:
            opts = info.project(opts)
            # ^  In case of an update read and parse setup.cfg inside project
        except Exception as e:
            raise NoPyScaffoldProject from e

    return opts
