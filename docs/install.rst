============
Installation
============

Requirements
============

The installation of PyScaffold only requires a recent version of `setuptools`_,
i.e. at least version 38.3, as well as a working installation of `Git`_.
Especially Windows users should make sure that the command ``git`` is available on
the command line. Otherwise, check and update your ``PATH`` environment
variable or run PyScaffold from the *Git Bash*.

.. note::

    If you plan to create a `Django`_ project or want to use
    `Cookiecutter`_ with PyScaffold, please have a look on the extensions:

    * Django - `pyscaffoldext-django`_
    * Cookiecutter - `pyscaffoldext-cookiecutter`_

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

If you want to install PyScaffold with all official extensions, run::

    pip install --upgrade pyscaffold[all]

PyScaffold is also available at `conda-forge`_ and thus can be installed with `conda`_::

    conda install -c conda-forge pyscaffold


Additional Requirements
=======================

If you run commands like ``py.test`` and ``make -C docs`` within your project,
some additional requirements like py.test and Sphinx may be required. It might
be the case you are already have them installed but this can be confusing
because these packages won't be available to other packages inside your virtual
environment.  In order to avoid this just install following packages inside
your virtual environment:

* `Sphinx <http://sphinx-doc.org/>`_
* `py.test <http://pytest.org/>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_

Alternatively, you can setup build automation with **tox**. An easy way to do
that is to generate your project passing the ``--tox`` option.
The commands ``tox`` and ``tox -e doc`` should be able to run your tests or
build your docs out of the box.

.. note::

    If you have problems using PyScaffold, please make sure you are using
    Python 3.6 or greater. You might be able to run PyScaffold on Python 3.5,
    however this method is not officially supported.


.. _setuptools: https://pypi.python.org/pypi/setuptools/
.. _Git: https://git-scm.com/
.. _virtualenv: https://virtualenv.readthedocs.org/
.. _Anaconda: https://www.anaconda.com/download/
.. _conda-forge: https://anaconda.org/conda-forge/pyscaffold
.. _conda: https://conda.io
.. _pyscaffoldext-django: https://github.com/pyscaffold/pyscaffoldext-django
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _Django: https://pypi.python.org/pypi/Django/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
