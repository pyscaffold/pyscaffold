.. _examples:

================
Usage & Examples
================

.. _quickstart:

Quickstart
==========

A single command is all you need to quickly start coding like a Python rockstar,
skipping all the difficult and tedious bits::

    putup my_project

This will create a new folder called ``my_project`` containing a
*perfect project template* with everything you need for getting things done.
Checkout out `this demo project`_, which was set up using Pyscaffold.

.. tip::
   .. versionadded:: 4.0
      We are trying out a brand new *interactive mode* that makes it
      even easier to use PyScaffold in its full potential.
      If you want to give it a shot, use the ``--interactive``, or simply ``-i`` option.

      The interactive command equivalent to the previous example is:
      ``putup -i my_project``.

You can ``cd`` into your new project and interact with it from the
command line after creating (or activating) an `isolated
development environment`_ (with virtualenv_, conda_ or your preferred tool),
and performing the usual editable_ install::

   pip install -e .

… all set and ready to go! Try the following in a Python shell:

.. code-block:: pycon

   >>> from my_project.skeleton import fib
   >>> fib(10)
   55

Or if you are concerned about performing package maintainer tasks, make sure to
have tox_ installed and see what we have prepared for you out of the box::

   tox -e docs  # to build your documentation
   tox -e build  # to build your package distribution
   tox -e publish  # to test your project uploads correctly in test.pypi.org
   tox -e publish -- --repository pypi  # to release your package to PyPI
   tox -av  # to list all the tasks available

The following figure demonstrates the usage of ``putup`` with the new experimental
interactive mode for setting up a simple project.
It uses the `--cirrus` flag to add CI support (via `Cirrus CI`_), and
tox_ to run automated project tasks like building a package file for
distribution (or publishing).

.. image:: gfx/demo.gif
    :alt: Creating a simple package with PyScaffold
    :target: https://asciinema.org/a/qzh5ZYKl1q5xYEnM4CHT04HdW?autoplay=1

Type ``putup -h`` to learn about :ref:`other things PyScaffold can do <features>` for your project,
and if you are not convinced yet, have a look on these :ref:`reasons to use PyScaffold <reasons>`.

There is also a `video tutorial`_ on how to develop a command-line application with the help of PyScaffold.

Notes
-----

#. PyScaffold's project template makes use of a dedicated ``src``
   folder to store all the package files meant for distribution (additional
   files like tests and documentation are kept in their own separated folders).
   You can find some comments and useful links about this design decision in
   our :ref:`FAQ <faq>`.

#. The ``pip install -e .`` command installs your project in editable_ mode,
   making it available in import statements as any other Python module.
   It might fail if your have an old version of Python's package manager and
   tooling in your current environment. Please make sure you are using the
   intended environment (either a `virtual environment`_ [*recommended*] or the
   default installation of Python in the operating system) and try to update
   them with ``python -m pip install -U pip setuptools``.

#. If you are using a `virtual environment`_, please remember to
   re-activate it everytime you close your shell, otherwise you will not be
   able to import your project in the REPL_. To check if you have already
   activated it you can run ``which python`` on Linux and OSX, ``where python``
   on the classical Windows command prompt, or ``Get-Command python`` on
   PowerShell.


Examples
========

Just a few examples to get you an idea of how easy PyScaffold is to use:

``putup my_little_project``
  The simplest way of using PyScaffold. A directory ``my_little_project`` is
  created with a Python package named exactly the same. The MIT license will be used.

``putup -i my_little_project``
  If you are unsure on how to use PyScaffold, or keep typing ``putup --help``
  all the time, the **experimental** ``--interactive`` (or simply ``-i``), is
  your best friend.
  It will open your default text editor with a file containing examples and
  explanations on how to use ``putup`` (think of it as an "editable" ``--help``
  text, once the file is saved and closed all the values you leave there are
  processed by PyScaffold). You might find some familiarities in the way this
  option works with ``git rebase -i``, including the capacity of choosing a
  different text editor by setting the ``EDITOR`` (or ``VISUAL``) environment
  variable in your terminal.

``putup skynet -l GPL-3.0-only -d "Finally, the ultimate AI!" -u https://sky.net``
  This will create a project and package named *skynet* licensed under the GPL3.
  The *description* inside ``setup.cfg`` is directly set to "Finally, the ultimate AI!"
  and the homepage to ``https://sky.net``.

``putup Scikit-Gravity -p skgravity -l BSD-3-Clause``
  This will create a project named *Scikit-Gravity* but the package will be
  named *skgravity* with license new-BSD [#ex1]_.

``putup youtub --django --pre-commit -d "Ultimate video site for hot tub fans"``
  This will create a web project and package named *youtub* that also includes
  the files created by `Django's <https://www.djangoproject.com/>`_
  ``django-admin`` [#ex2]_. The *description* in ``setup.cfg`` will be set and
  a file ``.pre-commit-config.yaml`` is created with a default setup for
  `pre-commit <https://pre-commit.com/>`_.

``putup thoroughly_tested --cirrus``
  This will create a project and package *thoroughly_tested* with files ``tox.ini``
  and ``.cirrus.yml`` for tox_ and
  `Cirrus CI <https://cirrus-ci.org/>`_.

``putup my_zope_subpackage --name my-zope-subpackage --namespace zope --package subpackage``
  This will create a project under the ``my_zope_subpackage`` directory with
  the *installation name* of ``my-zope-subpackage`` (this is the name used by
  pip_ and PyPI_), but with the following corresponding import statement::

    from zope import subpackage
    # zope is the namespace and subpackage is the package name

  To be honest, there is really only the `Zope project <https://www.zope.org/>`_
  that comes to my mind which is using this exotic feature of Python's packaging system.
  Chances are high, that you will never ever need a namespace package in your life.
  To learn more about namespaces in the Python ecosystem, check `PEP 420`_.


.. [#ex1] Notice the usage of `SPDX identifiers`_ for specifying the license
   in the CLI

.. [#ex2] Requires the installation of pyscaffoldext-django_.


.. _configuration:

Package Configuration
=====================

Projects set up with PyScaffold rely on `setuptools`_, and therefore can be
easily configured/customised via ``setup.cfg``. Check out the example below:

.. literalinclude:: ./example_setup.cfg
    :language: ini

You might also want to have a look on `pyproject.toml`_ for specifying
dependencies required during the build:

.. literalinclude:: ../src/pyscaffold/templates/pyproject_toml.template
    :language: toml

Please note PyScaffold will add some internal information to ``setup.cfg``,
we do that to make updates a little smarter.

.. note::
   To avoid splitting the configuration and build parameters among several
   files, PyScaffold uses the same file as `setuptools`_ (``setup.cfg``).
   Storing configuration in `pyproject.toml`_ is not supported.
   In the future, if the default build metadata location changes (as proposed
   by `PEP 621`_), PyScaffold will follow the same pattern.


.. _default-cfg:

PyScaffold's Own Configuration
==============================

PyScaffold also allows you to save your favourite configuration to a file that
will be automatically read every time you run ``putup``, this way you can avoid
always retyping the same command line options.

The locations of the configuration files vary slightly across platforms, but in
general the following rule applies:

- Linux: ``$XDG_CONFIG_HOME/pyscaffold/default.cfg`` with fallback to ``~/.config/pyscaffold/default.cfg``
- OSX: ``~/Library/Application Support/pyscaffold/default.cfg``
- Windows(≥7): ``%APPDATA%\pyscaffold\pyscaffold\default.cfg``

The file format resembles the ``setup.cfg`` generated automatically by
PyScaffold, but with only the ``metadata`` and ``pyscaffold`` sections, for
example:

.. code-block:: ini

    [metadata]
    author = John Doe
    author-email = john.joe@gmail.com
    license = MPL-2.0

    [pyscaffold]
    extensions =
        cirrus
        pre-commit

With this file in place, typing only::

    $ putup myproj

will have the same effect as if you had typed::

    $ putup --license MPL-2.0 --cirrus --pre-commit myproj

.. note::

    For the time being, only the following options are allowed in the config file:

    - **metadata** section: ``author``, ``author-email`` and ``license``
    - **pyscaffold** section: ``extensions`` (and associated opts)

    Options associated with extensions are the ones prefixed by an extension name.


To prevent PyScaffold from reading an existing config file, you can pass the
``--no-config`` option in the CLI. You can also save the given options when
creating a new project with the ``--save-config`` option. Finally, to read the
configurations from a location other then the default, use the ``--config PATH``
option. See ``putup --help`` for more details.

.. warning::

    *Experimental Feature* - We are still evaluating how this new and exciting
    feature will work, so its API (including file format and name) is not considered
    stable and might change between minor versions. As previously stated, if
    the configuration file for `setuptools`_ changes (e.g. with `PEP 621`_),
    PyScaffold will follow that and change its own configuration.

    This means that in future versions, PyScaffold will likely adopt a more
    `pyproject.toml`-style configuration (and as a consequence the file name
    and extension might change).


.. _setuptools: https://setuptools.pypa.io/en/stable/userguide/declarative_config.html
.. _pyproject.toml: https://setuptools.pypa.io/en/stable/build_meta.html
.. _PEP 621: https://www.python.org/dev/peps/pep-0621/
.. _SPDX identifiers: https://spdx.org/licenses/
.. _pyscaffoldext-django: https://pyscaffold.org/projects/django/en/stable/
.. _pip: https://pip.pypa.io/en/stable/
.. _PyPI: https://pypi.org
.. _PEP 420: https://www.python.org/dev/peps/pep-0420/
.. _video tutorial: https://www.youtube.com/watch?v=JwwlRkLKj7o
.. _this demo project: https://github.com/pyscaffold/pyscaffold-demo
.. _editable: https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs
.. _isolated development environment: https://realpython.com/python-virtual-environments-a-primer/
.. also good, but sometimes medium can get on the way: https://towardsdatascience.com/virtual-environments-104c62d48c54
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _conda: https://docs.conda.io/en/latest/
.. _REPL: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
.. _tox: https://tox.wiki/en/stable/
.. _Cirrus CI: https://cirrus-ci.org/
