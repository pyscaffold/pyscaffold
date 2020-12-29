"""
Templates for all files of a project's scaffold
"""

import os
import string
import sys
from types import ModuleType
from typing import Any, Dict, Set, Union

from configupdater import ConfigUpdater

from .. import __version__ as pyscaffold_version
from .. import dependencies as deps
from .. import toml

if sys.version_info[:2] >= (3, 7):
    # TODO: Import directly (no need for workaround) when `python_requires = >= 3.7`
    from importlib.resources import read_text  # pragma: no cover
else:
    from pkgutil import get_data  # pragma: no cover

    def read_text(package, resource, encoding="utf-8") -> str:  # pragma: no cover
        data = get_data(package, resource)
        if data is None:
            raise FileNotFoundError(f"{resource!r} resource not found in {package!r}")
        return data.decode(encoding)


ScaffoldOpts = Dict[str, Any]

#: All available licences (identifiers based on SPDX ``https://spdx.org/licenses/``)
licenses = {
    "MIT": "license_mit",
    "AGPL-3.0-or-later": "license_affero_3.0",
    "AGPL-3.0-only": "license_affero_3.0",
    "Apache-2.0": "license_apache",
    "Artistic-2.0": "license_artistic_2.0",
    "BSD-2-Clause": "license_simplified_bsd",
    "BSD-3-Clause": "license_new_bsd",
    "CC0-1.0": "license_cc0_1.0",
    "EPL-1.0": "license_eclipse_1.0",
    "GPL-2.0-or-later": "license_gpl_2.0",
    "GPL-2.0-only": "license_gpl_2.0",
    "GPL-3.0-or-later": "license_gpl_3.0",
    "GPL-3.0-only": "license_gpl_3.0",
    "ISC": "license_isc",
    "LGPL-2.0-or-later": "license_lgpl_2.1",
    "LGPL-2.0-only": "license_lgpl_2.1",
    "LGPL-3.0-or-later": "license_lgpl_3.0",
    "LGPL-3.0-only": "license_lgpl_3.0",
    "MPL-2.0": "license_mozilla",
    "Unlicense": "license_public_domain",
    # ---- not really in the SPDX license list ----
    "Proprietary": "license_none",
}
# order is relevant: -only licenses should come after -or-later, so they dominate
# MIT goes first so it behaves like the default if an empty string is passed


def get_template(
    name: str, relative_to: Union[str, ModuleType] = __name__
) -> string.Template:
    """Retrieve the template by name

    Args:
        name: name of template (the ``.template`` extension will be
            automatically added to this name)
        relative_to: module/package object or name to which the resource file
            is relative (in the standard module format, e.g. ``foo.bar.baz``).
            Notice that ``relative_to`` should not represent directly a shared
            namespace package, since this kind of package is spread in
            different folders in the file system.

            Default value: ``pyscaffold.templates``
            (**please assign accordingly when using in custom extensions**).

    Examples:
        Consider the following package organization::

            .
            ├── src
            │   └── my_package
            │       ├── __init__.py
            │       ├── templates
            │       │   ├── __init__.py
            │       │   ├── file1.template
            │       │   └── file2.template
            │       …
            └── tests

        Inside the file ``src/my_package/__init__.py``, one can easily obtain
        the contents of ``file1.template`` by doing:

        .. code-block:: python

            from pyscaffold.templates import get_template
            from . import templates as my_templates

            tpl1 = get_template("file1", relative_to=my_templates)
            # OR
            # tpl1 = get_template('file1', relative_to=my_templates.__name__)

    Please notice you can also use `relative_to=__name__`
    or a combination of `from .. import __name__ as parent` and
    `relative_to=parent` to deal with relative imports.

    Returns:
        :obj:`string.Template`: template

    .. versionchanged :: 3.3
        New parameter **relative_to**.
    """
    file_name = f"{name}.template"
    if isinstance(relative_to, ModuleType):
        relative_to = relative_to.__name__

    data = read_text(relative_to, file_name, encoding="utf-8")
    # we assure that line endings are converted to '\n' for all OS
    content = data.replace(os.linesep, "\n")
    return string.Template(content)


def setup_cfg(opts: ScaffoldOpts) -> str:
    """Template of setup.cfg

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("setup_cfg")
    cfg_str = template.substitute(opts)
    updater = ConfigUpdater()
    updater.read_string(cfg_str)
    requirements = deps.add(deps.RUNTIME, opts.get("requirements", []))
    updater["options"]["install_requires"].set_values(requirements)

    # fill [pyscaffold] section used for later updates
    add_pyscaffold(updater, opts)
    pyscaffold = updater["pyscaffold"]
    pyscaffold["version"].add_after.option("package", opts["package"])

    return str(updater)


def add_pyscaffold(config: ConfigUpdater, opts: ScaffoldOpts) -> ConfigUpdater:
    """Add PyScaffold section to a ``setup.cfg``-like file + PyScaffold's version +
    extensions and their associated options.
    """
    if "pyscaffold" not in config:
        config.add_section("pyscaffold")

    pyscaffold = config["pyscaffold"]
    pyscaffold["version"] = pyscaffold_version

    # Add the new extensions alongside the existing ones
    extensions = {ext.name for ext in opts.get("extensions", []) if ext.persist}
    old = pyscaffold.pop("extensions", "")
    old = parse_extensions(getattr(old, "value", old))  # coerce configupdater return
    pyscaffold.set("extensions")
    pyscaffold["extensions"].set_values(sorted(old | extensions))

    # Add extension-related opts, i.e. opts which start with an extension name
    allowed = {k: v for k, v in opts.items() if any(map(k.startswith, extensions))}
    pyscaffold.update(allowed)

    return config


def parse_extensions(extensions: str) -> Set[str]:
    """Given a string value for the field ``pyscaffold.extensions`` in a
    ``setup.cfg``-like file, return a set of extension names.
    """
    ext_names = (ext.strip() for ext in extensions.strip().split("\n"))
    return {ext for ext in ext_names if ext}


def pyproject_toml(opts: ScaffoldOpts) -> str:
    template = get_template("pyproject_toml")
    config = toml.loads(template.safe_substitute(opts))
    config["build-system"]["requires"] = list(deps.ISOLATED)
    return toml.dumps(config)


def license(opts):
    """Template of LICENSE.txt

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template(licenses[opts["license"]])
    return template.substitute(opts)


def init(opts):
    """Template of __init__.py

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    if opts["package"] == opts["name"]:
        opts["distribution"] = "__name__"
    else:
        opts["distribution"] = '"{}"'.format(opts["name"])
    template = get_template("__init__")
    return template.substitute(opts)
