
from subprocess import call

import os

if os.environ.get('TOXENV'):
    # normal tox run, lets jsut have tox do its job
    import tox
    tox.cmdline()
elif os.environ.get('SELFINSTALL'):
    # self install testing needs some clarity
    # so its being executed without any other tools running
    call('python setup.py sdist', shell=True)
    call('easy_install dist/*', shell=True)
    import pkg_resources
    dist = pkg_resources.get_distribution('setuptools_scm')
    assert set(dist.version) == set(".0"), dist.version
