============
Installation
============

Requirements
============

The installation of PyScaffold only requires a recent version of `setuptools`_,
i.e. at least version 30.3.0, as well as a working installation of `Git`_.
Especially Windows users should make sure that the command ``git`` is available on
the command line. Otherwise, check and update your ``PATH`` environment
variable or run PyScaffold from the *Git Bash*.

Additionally, if you want to create a Django project or want to use
cookiecutter:

* `Django <https://pypi.python.org/pypi/Django/>`_
* `Cookiecutter <https://cookiecutter.readthedocs.org/>`_

.. note::

    It is recommended to use an isolated environment as provided by `virtualenv`_
    or even better `Anaconda`_ for your work with Python in general.

Installation
============

Make sure you have ``pip`` installed, then simply type::

    pip install --upgrade pyscaffold

to get the latest stable version. The most recent development version can be
installed with::

    pip install --pre --upgrade pyscaffold

Using ``pip`` also has the advantage that all requirements are automatically
installed.

If you want to install PyScaffold with all features like Django and
cookiecutter support, run::

    pip install --upgrade pyscaffold[ALL]

PyScaffold is also available at `conda-forge`_ and thus can be installed with `conda`_::

    conda install -c conda-forge pyscaffold


Additional Requirements
=======================

If you run commands like ``python setup.py test`` and ``python setup.py docs``
within your project, some additional requirements like py.test will be
installed automatically as *egg*-files inside the ``.eggs`` folder. This is
quite comfortable but can be confusing because these packages won't be
available to other packages inside your virtual environment. In order to avoid
this just install following packages inside your virtual environment before you
run ``setup.py`` commands like *doc* and *test*:

* `Sphinx <http://sphinx-doc.org/>`_
* `py.test <http://pytest.org/>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_

.. _setuptools: https://pypi.python.org/pypi/setuptools/
.. _Git: https://git-scm.com/
.. _virtualenv: https://virtualenv.readthedocs.org/
.. _Anaconda: https://www.anaconda.com/download/
.. _conda-forge: https://anaconda.org/conda-forge/pyscaffold
.. _conda: https://conda.io
