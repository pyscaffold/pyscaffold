# -*- coding: utf-8 -*-
import shlex
from subprocess import STDOUT, check_output


def run(*args, **kwargs):
    # normalize args
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0])
        else:
            args = args[0]

    opts = dict(stderr=STDOUT, universal_newlines=True)
    opts.update(kwargs)

    return check_output(args, **opts)
