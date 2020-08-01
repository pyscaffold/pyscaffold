"""
Templates for all files of a project's scaffold
"""

import os
import string
from types import ModuleType
from typing import Any, Dict, Set, Union

from pkg_resources import resource_string

from configupdater import ConfigUpdater

from .. import __version__ as pyscaffold_version
from .. import dependencies as deps
from .. import toml

ScaffoldOpts = Dict[str, Any]

#: All available licences
licenses = {
    "affero": "license_affero_3.0",
    "apache": "license_apache",
    "artistic": "license_artistic_2.0",
    "cc0": "license_cc0_1.0",
    "eclipse": "license_eclipse_1.0",
    "gpl2": "license_gpl_2.0",
    "gpl3": "license_gpl_3.0",
    "isc": "license_isc",
    "lgpl2": "license_lgpl_2.1",
    "lgpl3": "license_lgpl_3.0",
    "mit": "license_mit",
    "mozilla": "license_mozilla",
    "new-bsd": "license_new_bsd",
    "none": "license_none",
    "proprietary": "license_none",
    "public-domain": "license_public_domain",
    "simple-bsd": "license_simplified_bsd",
}


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
            different folders in the file sytem.

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

            tpl1 = get_template('file1', relative_to=my_templates)
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

    data = resource_string(relative_to, file_name)
    # we assure that line endings are converted to '\n' for all OS
    content = data.decode(encoding="utf-8").replace(os.linesep, "\n")
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

    # add `classifiers`
    help = "Add here all kinds of additional classifiers as defined under"
    ref = "https://pypi.python.org/pypi?%3Aaction=list_classifiers"
    metadata = updater["metadata"]
    metadata["platforms"].add_after.comment(help).comment(ref).option("classifiers")
    metadata["classifiers"].set_values(opts["classifiers"])

    # add `setup_requires` and `install_requires`
    options = updater["options"]
    setup_requires = options["setup_requires"]
    setup_requires.set_values(list(deps.BUILD).copy())
    if opts["requirements"]:
        setup_requires.add_after.option("install_requires")
        options["install_requires"].set_values(list(opts["requirements"]).copy())
    else:
        help = "Add here dependencies of your project (semicolon/line-separated), e.g."
        example = "install_requires = numpy; scipy"
        setup_requires.add_after.comment(help).comment(example)

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
    config["build-system"]["requires"] = deps.ISOLATED
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
