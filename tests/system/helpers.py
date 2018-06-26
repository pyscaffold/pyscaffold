# -*- coding: utf-8 -*-
import shlex
from os import environ
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


def run_common_tasks(tests=True, flake8=True):
    if tests:
        run('python setup.py test')

    run('python setup.py doctest')
    run('python setup.py docs')
    run('python setup.py --version')
    run('python setup.py sdist')
    run('python setup.py bdist')

    if flake8 and environ.get('COVERAGE') == 'true':
        run('flake8 --count')
