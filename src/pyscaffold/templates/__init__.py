"""
Templates for all files of a project's scaffold
"""

import os
import string
from types import ModuleType

from pkg_resources import resource_string

from configupdater import ConfigUpdater

from .. import __version__ as pyscaffold_version
from ..utils import get_requirements_str

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


def get_template(name, relative_to=__name__):
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
    file_name = "{name}.template".format(name=name)
    if isinstance(relative_to, ModuleType):
        relative_to = relative_to.__name__

    data = resource_string(relative_to, file_name)
    # we assure that line endings are converted to '\n' for all OS
    data = data.decode(encoding="utf-8").replace(os.linesep, "\n")
    return string.Template(data)


def setup_cfg(opts):
    """Template of setup.cfg

    Args:
        opts: mapping parameters as dictionary

    Returns:
        str: file content as string
    """
    template = get_template("setup_cfg")
    opts["setup_requires_str"] = get_requirements_str()
    cfg_str = template.substitute(opts)

    updater = ConfigUpdater()
    updater.read_string(cfg_str)

    # add `classifiers`
    (
        updater["metadata"]["platforms"]
        .add_after.comment(
            "Add here all kinds of additional classifiers as defined under"
        )
        .comment("https://pypi.python.org/pypi?%3Aaction=list_classifiers")
        .option("classifiers")
    )
    updater["metadata"]["classifiers"].set_values(opts["classifiers"])

    # add `install_requires`
    setup_requires = updater["options"]["setup_requires"]
    if opts["requirements"]:
        setup_requires.add_after.option("install_requires")
        updater["options"]["install_requires"].set_values(opts["requirements"])
    else:
        (
            setup_requires.add_after.comment(
                "Add here dependencies of your project "
                "(semicolon/line-separated), e.g."
            ).comment("install_requires = numpy; scipy")
        )

    # fill [pyscaffold] section used for later updates
    pyscaffold = updater["pyscaffold"]
    pyscaffold["version"] = pyscaffold_version
    pyscaffold["package"] = opts["package"]
    if opts["cli_params"]["extensions"]:
        pyscaffold.set("extensions")
        pyscaffold["extensions"].set_values(opts["cli_params"]["extensions"])
        for extension, args in opts["cli_params"]["args"].items():
            pyscaffold[extension] = args

    return str(updater)


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
