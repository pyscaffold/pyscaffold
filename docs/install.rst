============
Installation
============

Requirements
============

The installation of PyScaffold requires:

* `setuptools <https://pypi.python.org/pypi/setuptools/>`_
* `six <https://pypi.python.org/pypi/six>`_

Additionally, if you want to create a Django project or want to use
cookiecutter:

* `Django <https://pypi.python.org/pypi/Django/>`_
* `cookiecutter <https://cookiecutter.readthedocs.org/>`_

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

If you want to install PyScaffold with all features like Django and
cookiecutter support, run::

    pip install --upgrade pyscaffold[ALL]


Additional Requirements
=======================

If you run commands like ``python setup.py test`` and ``python setup.py docs``
within your project, some additional requirements like py.test will be
installed automatically. This is quite comfortable on the one hand but will
also pollute your project with a lot of *egg*-folders. In order to avoid this
just install following packages inside your virtual environment before you run
*setup.py* commands like *doc* and *test*:

* `Sphinx <http://sphinx-doc.org/>`_
* `py.test <http://pytest.org/>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_
