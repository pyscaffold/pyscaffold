#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from pyscaffold import templates


def test_get_template():
    template = templates.get_template("setup_py")
    content = template.safe_substitute()
    assert content.split(os.linesep, 1)[0] == '# -*- coding: utf-8 -*-'


def test_all_licenses():
    opts = {"email": "test@user",
            "project": "my_project",
            "author": "myself",
            "year": 1832}
    for license in templates.licenses.keys():
        opts['license'] = license
        assert templates.license(opts)
