#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from pyscaffold import templates

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_get_template():
    template = templates.get_template("setup_py")
    content = template.safe_substitute()
    assert content.split(os.linesep, 1)[0] == '#!/usr/bin/env python'


def test_all_licenses():
    args = type("Namespace", (object,), dict())
    args.email = "test@user"
    args.project = "my_project"
    args.author = "myself"
    args.year = 1832
    for license in templates.licenses.keys():
        args.license = license
        assert templates.license(args)


def test_best_fit_license():
    txt = "new_bsd"
    assert templates.best_fit_license(txt) == "new-bsd"
    for license in templates.licenses.keys():
        assert templates.best_fit_license(license) == license
