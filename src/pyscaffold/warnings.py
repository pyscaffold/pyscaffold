# -*- coding: utf-8 -*-
"""
Warnings used by PyScaffold to identify issues that can be safely ignored
but that should be displayed to the user.
"""


class UpdateNotSupported(RuntimeWarning):
    """Extensions that make use of external generators are not able to do
    updates by default.
    """

    DEFAULT_MESSAGE = ('Updating code generated using external tools is not '
                       'supported. The extension `{}` will be ignored, only '
                       'changes in PyScaffold core features will take place.')

    def __init__(self, *args, extension=None, **kwargs):
        if not args:
            args = [self.DEFAULT_MESSAGE.format(extension)]
        super(UpdateNotSupported, self).__init__(*args, **kwargs)
