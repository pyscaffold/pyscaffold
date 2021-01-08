"""
Command-Line-Interface of PyScaffold
"""

import argparse
import logging
import sys
from typing import List, Optional, Tuple

from packaging.version import Version

from . import __version__ as pyscaffold_version
from . import api, templates
from .actions import ScaffoldOpts
from .actions import discover as discover_actions
from .dependencies import check_setuptools_version
from .exceptions import exceptions2exit
from .extensions import list_from_entry_points as list_all_extensions
from .identification import get_id
from .info import best_fit_license
from .log import ReportFormatter, logger
from .shell import shell_command_error2exit_decorator


def add_log_related_args(parser: argparse.ArgumentParser):
    """Add options that control verbosity/logger level"""
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="log_level",
        help="show additional information about current actions",
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="show all available information about current actions",
    )
    parser.add_argument(
        "-P",
        "--pretend",
        dest="pretend",
        action="store_true",
        default=False,
        help="do not create project, but displays the log of all operations"
        " as if it had been created.",
    )


def add_default_args(parser: argparse.ArgumentParser):
    """Add the default options and arguments to the CLI parser."""

    # Here we can use api.DEFAULT_OPTIONS to provide the help text, but we should avoid
    # passing a `default` value to argparse, since that would shadow
    # `api.bootstrap_options`.
    # Setting defaults with `api.bootstrap_options` guarantees we do that in a
    # centralised manner, that works for both CLI and direct Python API invocation.
    parser.add_argument(
        dest="project_path",
        help="path where to generate/update project",
        metavar="PROJECT_PATH",
    )
    parser.add_argument(
        "-n",
        "--name",
        dest="name",
        required=False,
        help="installable name "
        "(as in `pip install`/PyPI, default: basename of PROJECT_PATH)",
        metavar="NAME",
    )
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        required=False,
        help="package name (as in `import`, default: NAME)",
        metavar="PACKAGE_NAME",
    )
    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        required=False,
        help="package description",
        metavar="TEXT",
    )
    license_choices = list(templates.licenses.keys())
    choices_help = ", ".join(license_choices)
    default_license = api.DEFAULT_OPTIONS["license"]
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        type=best_fit_license,
        required=False,
        help=f"package license like {choices_help} (default: {default_license})",
        metavar="LICENSE",
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        help="main website/reference URL for package",
        metavar="URL",
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        required=False,
        help="force overwriting an existing directory",
    )
    parser.add_argument(
        "-U",
        "--update",
        dest="update",
        action="store_true",
        required=False,
        help="update an existing project by replacing the most important files"
        " like setup.py etc. Use additionally --force to replace all scaffold files.",
    )

    # The following are basically for the CLI options, so having a default value is OK.
    parser.add_argument(
        "-V", "--version", action="version", version=f"PyScaffold {pyscaffold_version}"
    )

    add_log_related_args(parser)
    # ^  Even if these options are never processed here this guarantees they
    #    are displayed with --help

    parser.add_argument(
        "--list-actions",
        dest="command",
        action="store_const",
        const=list_actions,
        help="do not create project, but show a list of planned actions",
    )


def add_extension_args(parser: argparse.ArgumentParser):
    """Add options and arguments defined by extensions to the CLI parser."""
    # load and instantiate extensions
    cli_extensions = list_all_extensions()

    for extension in cli_extensions:
        extension.augment_cli(parser)


def process_log_related_args(args: List[str]) -> Tuple[List[str], ScaffoldOpts]:
    # See #378
    """We need to parse the log_level first, before the extensions are loaded,
    so the user can debug errors by setting the correct level.

    As a side-effect, this function will change the PyScaffold's logger level.
    """
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.set_defaults(log_level=logging.WARNING)
    add_log_related_args(pre_parser)

    parsed_args, remaining_args = pre_parser.parse_known_args(args)
    partial_opts = vars(parsed_args)
    logger.reconfigure(partial_opts)
    partial_opts["log_level"] = logger.level  # update with processed value
    return remaining_args, partial_opts


def parse_args(args: List[str]) -> ScaffoldOpts:
    """Parse command line parameters respecting extensions

    Args:
        args: command line parameters as list of strings

    Returns:
        dict: command line parameters
    """
    # Process log_level first, so if errors happen they are correctly displayed
    remaining_args, log_related_opts = process_log_related_args(args)

    # Create the actual argument parser, with all the options
    msg = "PyScaffold is a tool for easily putting up the scaffold of a Python project."
    parser = argparse.ArgumentParser(description=msg)
    parser.set_defaults(extensions=[], config_files=[], command=run_scaffold)

    add_default_args(parser)
    add_extension_args(parser)

    # -- Parse options and transform argparse Namespace object into common dict
    # Please not that there are many places where you can process scaffold options.
    # We should only do the absolutely minimum necessary in the CLI-layer.
    # Default values should go to :obj:`pyscaffold.api.bootstrap_options` and derived
    # values should go to :obj:`pyscaffold.actions.get_default_options`.
    # This is important to keep feature parity between CLI and Python-only API.
    opts = vars(parser.parse_args(remaining_args))
    return _ensure_setdefault_works({**opts, **log_related_opts})


def _ensure_setdefault_works(opts):
    return {k: v for k, v in opts.items() if v not in (None, "")}
    # ^  Remove empty items


def run_scaffold(opts: ScaffoldOpts):
    """Actually scaffold the project, calling the python API

    Args:
        opts (dict): command line options as dictionary
    """
    api.create_project(opts)
    if opts["update"] and not opts["force"]:
        note = (
            "Update accomplished!\n"
            "Please check if your setup.cfg still complies with:\n"
            "https://pyscaffold.org/en/v{}/configuration.html"
        )
        base_version = Version(pyscaffold_version).base_version
        print(note.format(base_version))


def list_actions(opts: ScaffoldOpts):
    """Do not create a project, just list actions considering extensions

    Args:
        opts (dict): command line options as dictionary
    """
    actions = discover_actions(opts.get("extensions", []))

    print("Planned Actions:")
    for action in actions:
        print(ReportFormatter.SPACING + get_id(action))


def main(args: List[str]):
    """Main entry point for external applications

    Args:
        args: command line arguments
    """
    check_setuptools_version()
    opts = parse_args(args)
    opts["command"](opts)


@shell_command_error2exit_decorator
@exceptions2exit([RuntimeError])
def run(args: Optional[List[str]] = None):
    """Entry point for console script"""
    main(args or sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
