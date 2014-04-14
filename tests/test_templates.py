#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import templates

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_get_template():
    content = templates.get_template("setup")
    assert content.split("\n", 1)[0] == '#!/usr/bin/env python'
