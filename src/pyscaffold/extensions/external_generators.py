# -*- coding: utf-8 -*-
"""
Add extensions that use external generators in a mutually exclusive fashion.
"""
from __future__ import absolute_import

from . import cookiecutter, django
from ..api import Extension


class ExternalGenerators(Extension):
    """Handle external generatos like Django and Cookiecutter"""
    def augment_cli(self, parser):
        """Add generators in a way they cannot be called together.

        Args:
            parser: current parser object
        """
        group = parser.add_mutually_exclusive_group()
        cookiecutter.augment_cli(group)
        django.augment_cli(group)

    def activate(self, _):
        """Dummy implemented that will never be called"""
        raise RuntimeError("Implemented but never called!")
