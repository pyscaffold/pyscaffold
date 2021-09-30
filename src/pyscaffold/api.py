"""
External API for accessing PyScaffold programmatically via Python.
"""
from enum import Enum
from functools import reduce
from pathlib import Path

from . import __version__ as VERSION
from . import actions, info
from .exceptions import DirectErrorForUser, NoPyScaffoldProject

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
    "license": "MIT",
    "version": VERSION,
    "extensions": [],
    "config_files": [],  # Overloaded in bootstrap_options for lazy evaluation
}
"""Default values for PyScaffold's options.

Options that can be derived from the values of other options (e.g. ``package`` can be
derived from ``project_path`` when not explicitly passed) are computed in
:obj:`pyscaffold.actions.get_default_options`.

When ``config_files`` is empty, a default value is computed dynamically by
:obj:`pyscaffold.info.config_file` before the start of PyScaffold's action pipeline.

Warning:
    Default values might be dynamically overwritten by ``config_files`` or, during
    updates, existing ``setup.cfg``.
"""


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

    opts["version"] = VERSION  # always update version
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

    :Project Information:   - **project_path** (:obj:`os.PathLike` or :obj:`str`)

    :Naming:                - **name** (*str*): as in ``pip install`` or in PyPI
                            - **package** (*str*): Python identifier as in ``import``
                              (without namespace)

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
                            - **config_files** (*list* or ``NO_CONFIG``)

    Some of these options are equivalent to the command line options, others
    are used for creating the basic python package meta information, but the
    ones in the "PyScaffold Control" group affects how the "scaffolding" behaves.

    When the **force** flag is ``True``, existing files will be overwritten.
    When the **update** flag is ``True``, PyScaffold will consider that some
    files can be updated (usually the packaging boilerplate),
    but will keep others intact.
    When the **pretend** flag is ``True``, the project will not be
    created/updated, but the expected outcome will be logged.

    The **extensions** list may contain any object that follows the
    :ref:`extension API <extensions>`. Note that some PyScaffold features, such
    as cirrus, tox and pre-commit support, are implemented as built-in
    extensions. In order to use these features it is necessary to include the
    respective objects in the extension list. All built-in extensions are
    accessible via :mod:`pyscaffold.extensions` submodule.

    Finally, when ``setup.cfg``-like files are added to the **config_files** list,
    PyScaffold will read it's options from there in addition to the ones already passed.
    If the list is empty, the default configuration file is used. To avoid reading any
    existing configuration, please pass ``config_file=NO_CONFIG``.
    See :doc:`usage </usage>` for more details.

    Note that extensions may define extra options. For example, the
    cookiecutter extension define a ``cookiecutter`` option that
    should be the address to the git repository used as template and the ``namespace``
    extension define a ``namespace`` option with the name of a PEP 420 compatible
    (and possibly nested) namespace.
    """
    opts = bootstrap_options(opts, **kwargs)
    pipeline = actions.discover(opts["extensions"])

    # call the actions to generate final struct and opts
    return reduce(actions.invoke, pipeline, ({}, opts))


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
        opts = reduce(info.project, deduplicated.keys(), opts)

    if opts.get("update"):
        try:
            opts = info.project(opts)
            # ^  In case of an update read and parse setup.cfg inside project
        except DirectErrorForUser:
            raise
        except Exception as e:
            raise NoPyScaffoldProject from e

    return opts
