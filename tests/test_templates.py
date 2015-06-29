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
    opts = {"email": "test@user",
            "project": "my_project",
            "author": "myself",
            "year": 1832}
    for license in templates.licenses.keys():
        opts['license'] = license
        assert templates.license(opts)
