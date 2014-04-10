#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyscaffold import templates


def test_get_template():
    content = templates.get_template("setup")
    assert isinstance(content, str)
