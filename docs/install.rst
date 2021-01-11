.. _installation:

============
Installation
============

Requirements
============

The installation of PyScaffold only requires a recent version of of `setuptools`_,
(at least version 46.1), pip_, as well as a `working installation of Git`_
(meaning at least your *name and email were configured* in your first-time `git setup`_).
Especially Windows users should make sure that the command ``git`` is available on
the command line. Otherwise, check and update your ``PATH`` environment
variable or run PyScaffold from the *Git Bash*.

.. tip::
   It is recommended to use an `isolated development environment`_ as provided
   by `virtualenv`_ or `conda`_ for your work with Python in general. You
   might want to install PyScaffold globally in your system, but consider
   using virtual environments when developing your packages.

Installation
============

PyScaffold relies on a Python package manager for its installation.
The easiest way of getting started is via our loved `pip`_.
Make sure you have ``pip`` installed [#inst1]_, then simply type::

    pip install --upgrade pyscaffold

to get the latest stable version. The most recent development version can be
installed with::

    pip install --pre --upgrade pyscaffold

Using ``pip`` also has the advantage that all requirements are automatically
installed.

If you want to install PyScaffold with all official extensions, run::

    pip install --upgrade pyscaffold[all]


Alternative Methods
===================

It is very easy to get PyScaffold installed with `pip`_, but some people do
prefer other package managers such as `conda`_ while doing their work.

If you do lots of number crunching or data science in general [#inst2]_ and you already
rely on `conda-forge`_ packages, you might also use the following method::

    conda install -c conda-forge pyscaffold

It is also very common for developers to have more then one Python version
installed on their machines, and a plethora of virtual environments spread all
over the place… Instead of constantly re-installing PyScaffold in each one of
these installations and virtual environments, you can use `pipx`_ to do a
"minimally-invasive" system-wide installation and have the ``putup`` command
always available independently of which Python you are using::

    pipx install pyscaffold

Please check the documentation of each tool to understand how they work with
extra requirements (e.g. ``[all]``) or how to add extensions (e.g. ``pipx
inject pyscaffold pyscaffoldext-dsproject``).


Additional Requirements
=======================

We strongly recommend installing `tox`_ together with PyScaffold (both can be installed
with pip_, conda_ or pipx_), so you can take advantage of its automation
capabilities and avoid having to install dependencies/requirements manually.
If you do that, just by running the commands ``tox`` and ``tox -e docs``, you
should able to run your tests or build your docs out of the box (a list with
all the available tasks is obtained via the ``tox -av`` command).

If you dislike tox_, or are having problems with it, you can run commands (like
``pytest`` and ``make -C docs``) manually within your project, but then you
will have to deal with additional requirements and dependencies yourself.
It might be the case you are already have them installed but
this can be confusing because these packages won't be available to other
packages when you use a virtual environment. If that is the case,
just install following packages inside the environment you are using for
development:

* `Sphinx <http://sphinx-doc.org/>`_
* `pytest <http://pytest.org/>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_


.. note::
   If you have problems using PyScaffold, please make sure you are using
   Python 3.6 or greater.


.. [#inst1] In some operating systems, e.g. Ubuntu, this means installing a
   ``python3-pip`` package or similar via the OS's global package manager.

.. [#inst2] `conda`_ is a very competent package manager for Python, not only when you
   have to deal with numbers. In general, when you rely on native extensions,
   hardware acceleration or lower level programming languages integration (such
   as C or C++), `conda`_ might just be the tool you are looking for.


.. _working installation of Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _git setup: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
.. _setuptools: https://pypi.python.org/pypi/setuptools/
.. _pip: https://pip.pypa.io/en/stable/
.. _tox: https://tox.readthedocs.org/
.. _Git: https://git-scm.com/
.. _isolated development environment: https://realpython.com/python-virtual-environments-a-primer/
.. also good, but sometimes medium can get on the way: https://towardsdatascience.com/virtual-environments-104c62d48c54
.. _virtualenv: https://virtualenv.readthedocs.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _conda: https://conda.io
.. _conda-forge: https://anaconda.org/conda-forge/pyscaffold
.. _pipx: https://pipxproject.github.io/pipx/
.. _Django: https://pypi.python.org/pypi/Django/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
