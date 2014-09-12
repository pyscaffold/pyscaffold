============
Installation
============

Requirements
============

The installation of PyScaffold requires:

* `setuptools <https://pypi.python.org/pypi/setuptools/>`_
* `six <https://pypi.python.org/pypi/six>`_
* `pytest <https://pypi.python.org/pypi/pytest/>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov/>`_

Additionally, if you want to create a Django project:

* `Django <https://pypi.python.org/pypi/Django/>`_

.. note::

    In most cases only Django needs to be installed manually since PyScaffold
    will download and install its requirements automatically when using
    ``pip``. Once exception might be *setuptools*. If you use a current version
    of `Virtual Environments <http://docs.python-guide.org/en/latest/dev/
    virtualenvs/>`_ as development environment a current version should already
    be installed. In case you are using the system installation of Python
    from your Linux distribution make sure *setuptools* is installed.
    To install it on Debian or Ubuntu::

        sudo apt-get install python-setuptools


Installation
============

If you have ``pip`` installed, then simply type::

    pip install --upgrade pyscaffold

to get the lastest stable version. The most recent development version can be
installed with::

    pip install --pre --upgrade pyscaffold

Using ``pip`` also has the advantage that all requirements are automatically
installed.
