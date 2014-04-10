# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
from datetime import date
from string import Template
from os.path import join as join_path

from . import templates
from . import info


def gitignore():
    template = Template(templates.get_gitignore())
    return template.substitute()


def gitignore_all():
    return """\
# Ignore everything in this directory
*
# Except this file
!.gitignore
"""


def sphinx_index(args):
    title = args.project + "\n" + "="*len(args.project)
    template = Template(templates.get_sphinx_index())
    return template.substitute(title=title, project=args.project)


def sphinx_conf(args):
    dct = {"project": args.project,
           "package": args.package,
           "author": info.username(),
           "year": date.today().year}
    template = Template(templates.get_sphinx_conf())
    return template.substitute(dct)


def sphinx_makefile():
    return templates.get_sphinx_makefile()


def authors():
    dct = {"author": info.username(),
           "email": info.email()}
    template = Template(templates.get_authors())
    return template.substitute(dct)


def readme(args):
    title = args.project + "\n" + "="*len(args.project)
    template = Template(templates.get_readme())
    return template.substitute(project_title=title)


def manifest_in(args):
    template = Template(templates.get_manifest_in())
    return template.substitute(vars(args))


def setup(args):
    dct = vars(args).copy()
    dct["host"] = info.email().rsplit("@", 1)[1]
    dct["author"] = info.username()
    dct["email"] = info.email()
    template = Template(templates.get_setup())
    return template.substitute(dct)


def versioneer():
    return templates.get_versioneer()


def _version(args):
    template = Template(templates.get_version())
    return template.safe_substitute(vars(args))


def requirements():
    return templates.get_requirements()


def copying():
    return templates.get_copying()


def make_structure(args):
    struct = {args.project: {".gitignore": gitignore(),
                             args.package: {"__init__.py": "",
                                            "_version.py": _version(args)},
                             "tests": {"__init__.py": ""},
                             "docs": {"conf.py": sphinx_conf(args),
                                      "index.rst": sphinx_index(args),
                                      "Makefile": sphinx_makefile(),
                                      "_static": {
                                          ".gitignore": gitignore_all()}},
                             "README.rst": readme(args),
                             "AUTHORS.rst": authors(),
                             "MANIFEST.in": manifest_in(args),
                             "COPYING": copying(),
                             "setup.py": setup(args),
                             "versioneer.py": versioneer(),
                             "requirements.txt": requirements()}}
    return struct


def create_structure(struct, prefix=None):
    if prefix is None:
        prefix = os.getcwd()
    for name, content in struct.iteritems():
        if isinstance(content, str):
            with open(join_path(prefix, name), "w") as fh:
                fh.write(content)
        elif isinstance(content, dict):
            os.mkdir(join_path(prefix, name))
            create_structure(struct[name], prefix=join_path(prefix, name))
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))
