============
Installation
============

Requirements
============

The installation of PyScaffold requires:

* `setuptools <https://pypi.python.org/pypi/setuptools/>`_
* `six <https://pypi.python.org/pypi/six>`_

Additionally, if you want to create a Django project:

* `Django <https://pypi.python.org/pypi/Django/>`_

.. note::

    In most cases only Django needs to be installed manually since PyScaffold
    will download and install its requirements automatically when using
    ``pip``. One exception might be *setuptools* if you are not using a current
    version of `Virtual Environments <http://docs.python-guide.org/en/latest
    /dev/virtualenvs/>`_ as development environment.
    In case you are using the system installation of Python from your Linux
    distribution make sure *setuptools* is installed.
    To install it on Debian or Ubuntu::

        sudo apt-get install python-setuptools

    In case of Redhat or Fedora::

        sudo yum install python-setuptools

Installation
============

If you have ``pip`` installed, then simply type::

    pip install --upgrade pyscaffold

to get the lastest stable version. The most recent development version can be
installed with::

    pip install --pre --upgrade pyscaffold

Using ``pip`` also has the advantage that all requirements are automatically
installed.
