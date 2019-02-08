# -*- coding: utf-8 -*-
from uuid import uuid4


def uniqstr():
    """Generates a unique random long string every time it is called"""
    return str(uuid4())
