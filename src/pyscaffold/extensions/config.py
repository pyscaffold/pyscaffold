"""CLI options for using/saving preferences as PyScaffold config files."""
import argparse
from pathlib import Path
from typing import TYPE_CHECKING, List

from configupdater import ConfigUpdater

from .. import api, info, operations, templates
from . import Extension, store_with

if TYPE_CHECKING:  # pragma: no cover
    from ..actions import Action, ActionParams, ScaffoldOpts, Structure


class Config(Extension):
    """Add a few useful options for creating/using PyScaffold config files."""

    persist = False

    def augment_cli(self, parser: argparse.ArgumentParser):
        default_file = info.config_file(default=None)
        default_help = f" (defaults to: {default_file})" if default_file else ""
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--config",
            dest="config_files",
            metavar="CONFIG_FILE",
            nargs="+",
            type=Path,
            help=f"config file to read PyScaffold's preferences{default_help}",
        )
        group.add_argument(
            "--no-config",
            dest="config_files",
            action="store_const",
            const=api.NO_CONFIG,
            help="prevent PyScaffold from reading its default config file",
        )
        parser.add_argument(
            "--save-config",
            dest="save_config",
            action=store_with(self),
            nargs="?",
            const=default_file,
            default=argparse.SUPPRESS,
            type=Path,
            help=f"save the given options in a config file{default_help}",
        )
        return self

    def activate(self, actions: List["Action"]) -> List["Action"]:
        return actions[:-1] + [save, actions[-1]]  # Just before the last action


def save(struct: "Structure", opts: "ScaffoldOpts") -> "ActionParams":
    """Save the given opts as preferences in a PyScaffold's config file."""
    config = ConfigUpdater()

    if not opts.get("save_config"):
        file = info.config_file()
    else:
        file = Path(opts["save_config"])

    if file.exists():
        config.read(file, encoding="utf-8")
    else:
        config.read_string(
            "# PyScaffold's configuration file, see:\n"
            "# https://pyscaffold.org/en/latest/configuration.html\n#\n"
            "# Accepted in `metadata`: author, author_email and license.\n"
            "# Accepted in `pyscaffold`: extensions (and associated opts).\n"
        )

    if "metadata" not in config:
        config.add_section("metadata")

    # We will add metadata just if they are not the default ones
    metadata = config["metadata"]
    defaults = [
        ("author", opts["author"], info.username()),
        ("author_email", opts["email"], info.email()),
        ("license", opts["license"], api.DEFAULT_OPTIONS["license"]),
    ]

    metadata.update({k: v for k, v, default in defaults if v != default})
    templates.add_pyscaffold(config, opts)

    operations.create(file, str(config), opts)  # operations provide logging and pretend

    return struct, opts
