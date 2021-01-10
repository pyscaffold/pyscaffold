.. _dependencies:

=====================
Dependency Management
=====================

.. warning::

    *Experimental Feature* - PyScaffold support for `virtual environment`_
    management is experimental and might change in the future.

The greatest advantage in packaging Python code (when compared to other forms
of distributing programs and libraries) is that packages allow us to stand on
the shoulders of giants: you don't need to implement everything by yourself,
you can just declare dependencies on third-party packages and ``setuptools``,
``pip``, PyPI and their friends will do the heavy lifting for you.

Of course, with great power comes great responsibility. Package authors must be
careful when declaring the versions of the packages they depend on, so the
people consuming the final work can do reliable installations, without facing
dependency hell. In the opensource community, two main strategies have emerged
in the last few years:

* the first one is called **abstract** and consists of having permissive,
  minimal and generic dependencies, with versions specified by ranges, so
  anyone can install the package without many conflicts, sharing and reusing as
  much as possible dependencies that are already installed or are also required
  by other packages

* the second, called **concrete**, consists of having strict dependencies,
  with pinned versions, so all the users will have repeatable installations

Both approaches have advantages and disadvantages, and usually are used
together in different phases of a project. As a rule of thumb, libraries tend
to emphasize abstract dependencies (but can still have concrete dependencies
for the development environment), while applications tend to rely on concrete
dependencies (but can still have abstract dependencies specially if they are
intended to be distributed via PyPI, e.g. command line tools and auxiliary WSGI
apps/middleware to be mounted inside other domain-centric apps).
For more information about this topic check `Donald Stufft`_ post.

Since PyScaffold aims the development of Python projects that can be easily
packaged and distributed using the standard PyPI and ``pip`` flow, we adopt the
specification of **abstract dependencies** using |install_requires|_. This
basically means that if PyScaffold generated projects specify dependencies
inside the ``setup.cfg`` file (using general version ranges), everything will
work as expected.

.. _Donald Stufft: https://caremad.io/posts/2013/07/setup-vs-requirement/
.. |install_requires| replace:: ``setuptools``' ``install_requires``
.. _install_requires: https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies
.. _virtual environment: https://towardsdatascience.com/virtual-environments-104c62d48c54


Test Dependencies
=================

While specifying the final dependencies for packages is pretty much
straightforward (you just have to use ``install_requires`` inside
``setup.cfg``), dependencies for running the tests can be a little bit trick.

Historically, ``setuptools`` provides a ``tests_require`` field that follows
the same convention as ``install_requires``, however this field is not strictly
enforced, and ``setuptools`` doesn't really do much to enforce the packages
listed will be installed before the test suite runs.

PyScaffold's recommendation is to create a ``testing`` field (actually you can
name it whatever you want, but let's be explicit!) inside the
``[options.extras_require]`` section of ``setup.cfg``. This way multiple test
runners can have a centralised configuration and authors can avoid double
bookkeeping.

If you use ``tox`` (recommended), you can list ``testing`` under the |extras|_ option
(PyScaffold template for ``tox.ini`` already takes care of this configuration for you).

If running ``pytest`` directly, you will have to install those dependencies
manually, or do a editable install of your package with
``pip install -e .[testing]``.

.. tip:: If you prefer to use just ``tox`` and keep everything inside
    ``tox.ini``, please go ahead and move your test dependencies.
    Every should work just fine :)

.. note:: PyScaffold strongly advocates the use of test runners to guarantee
    your project is correctly packaged/works in isolated environments.
    New projects will ship with a default ``tox.ini`` file that is a good
    starting point, with a few useful tasks. Run ``tox -av`` to list all the
    available tasks.

.. |extras| replace:: the ``extras`` configuration field
.. _extras: http://tox.readthedocs.io/en/latest/config.html#confval-extras=MULTI-LINE-LIST


Development Environment
=======================

As previously mentioned, PyScaffold will get you covered when specifying the
**abstract** or test dependencies of your package. We provide sensible
configurations for ``setuptools`` and ``tox`` out-of-the-box.
In most of the cases this is enough, since developers in the
Python community are used to rely on tools like |virtualenv|_ and have a
workflow that take advantage of such configurations. As an example, someone
could do:

.. code-block:: bash

    $ pip install pyscaffold
    $ putup myproj
    $ cd myproj
    $ virtualenv .venv
    # OR python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -U pip setuptools setuptools_scm tox
    # ... edit setup.cfg to add dependencies ...
    $ pip install -e .
    $ tox

.. TODO: Remove the manual installation/update of pip, setuptools and setuptools_scm
   once pip starts supporting editable installs with pyproject.toml

However, someone could argue that this process is pretty manual and laborious
to maintain specially when the developer changes the **abstract** dependencies.

PyScaffold can alleviate this pain a little bit with the
:obj:`~pyscaffold.extensions.venv` extension:

.. code-block:: bash

    $ putup myproj --venv --venv-install PACKAGE
    # Is equivalent of running:
    #
    #     putup myproj
    #     cd myproj
    #     virtualenv .venv OR python -m venv .venv
    #     pip install PACKAGE

But it is still desirable to keep track of the version of each item in the
dependency graph, so the developer can have environment reproducibility when
trying to use another machine or discuss bugs with colleagues.

In the following sections, we describe how to use two popular command line
tools, supported by PyScaffold, to tackle these issues.

.. tip::
   When called with the ``--venv`` option, PyScaffold will try first to use
   |virtualenv|_ (there are some advantages on using it, such as being faster),
   and if it is not installed, will fallback to Python stdlib's :mod:`venv`.
   Plese notice however that even :mod:`venv` might not be available by default
   in your system: some OS/distributions split Python's stdlib in several
   packages and require the user to explicitly install them (e.g. Ubuntu will
   require you to do ``apt install python3-venv``). If you run into problems,
   try installing |virtualenv|_ and run the command again.

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/stable/


How to integrate Pipenv
-----------------------

We can think in `Pipenv`_ as a virtual environment manager. It creates
per-project virtualenvs and generates a ``Pipfile.lock`` file that contains a
precise description of the dependency tree and enables re-creating the exact
same environment elsewhere.

Pipenv supports two different sets of dependencies: the default one, and the
`dev` set. The default set is meant to store runtime dependencies while the dev
set is meant to store dependencies that are used only during development.

This separation can be directly mapped to PyScaffold strategy: basically the
default set should mimic the ``install_requires`` option in ``setup.cfg``,
while the dev set should contain things like ``tox``, ``sphinx``,
``pre-commit``, ``ptpython`` or any other tool the developer uses while
developing.

.. tip:: Test dependencies are internally managed by the test runner,
    so we don't have to tell Pipenv about them.

The easiest way of doing so is to add a ``-e .`` dependency (in resemblance
with the non-automated workflow) in the default set, and all the other ones in
the dev set. After using Pipenv, you should add both ``Pipfile`` and
``Pipfile.lock`` to your git repository to achieve reproducibility (maintaining
a single ``Pipfile.lock`` shared by all the developers in the same project can
save you some hours of sleep).

In a nutshell, PyScaffold+Pipenv workflow looks like:

.. code-block:: bash

    $ pip install pyscaffold pipenv
    $ putup myproj
    $ cd myproj
    # ... edit setup.cfg to add dependencies ...
    $ pipenv install
    $ pipenv install -e .  # proxy setup.cfg install_requires
    $ pipenv install --dev tox sphinx  # etc
    $ pipenv run tox       # use `pipenv run` to access tools inside env
    $ pipenv lock          # to generate Pipfile.lock
    $ git add Pipfile Pipfile.lock

After adding dependencies in ``setup.cfg``, you can run ``pipenv update`` to
add them to your virtual environment.

.. warning::

    *Experimental Feature* - `Pipenv`_ is still a young project that is moving
    very fast. Changes in the way developers can use it are expected in the
    near future, and therefore PyScaffold support might change as well.

.. _Pipenv: https://pipenv.pypa.io/


..
    TODO: As reported in issue https://github.com/jazzband/pip-tools/issues/204,
    pip-tools is generating absolute file paths inside ``requirements.txt``
    for ``-e .``, which prevents adding concrete dependencies to the repository
    and therefore misses the whole point of using such tool.
    For the time being, ``-e file:.`` seems to be a good workaround.
    We need to monitor the issue and them update accordingly

How to integrate ``pip-tools``
------------------------------

Contrary to Pipenv, |pip-tools|_ does not replace entirely the aforementioned
"manual" workflow. Instead, it provides lower level command line tools that
can be integrated to it, in order to achieve better reproducibility.

The idea here is that you have two types files describing your dependencies:
``*requirements.in`` and ``*requirements.txt``. The ``.in`` files are the ones
used to list **abstract** dependencies, while the ``.txt`` files are
generated by running ``pip-compile``.

Again the easiest way of having the ``requirements.in`` file to mimic
``setup.cfg``' ``install_requires`` is to add *something like* ``-e .`` to it.

.. warning::
   For the time being adding ``-e file:.`` is a working
   solution that is tested by |pip-tools|_ team (``-e .`` will generate absolute
   file paths in the compiled file, which will make it impossible to share).
   However this situation might change in the near future.
   You can find more details about this topic and monitor any changes in
   https://github.com/jazzband/pip-tools/issues/204.

   When using ``-e file:.`` in your ``requirements.in`` file,
   the compiled ``requirements.txt`` needs to be installed via
   ``pip-sync`` instead of ``pip install -r requirements.txt``


You can also create multiple environments and have multiple *"profiles"*, by using
different files, e.g. ``dev-requirements.in`` or ``ci-requirements.in``,
but keeping it simple and using ``requirements.in`` to represent all the tools
you need to run common tasks in a development environment is a good practice,
since you can omit the arguments when calling ``pip-compile`` and ``pip-sync``.
After all, if you need to have a separated test environment you can use tox,
and the minimal dependencies of your packages are already listed in
``setup.cfg``.

.. note::
   The existence of a ``requirements.txt`` file in the root of your repository
   does not imply all the packages listed there will be considered direct
   dependencies of your package. This was valid for older versions of
   PyScaffold (≤ 3), but is no longer the case. If the file exists, it is
   completely ignored by PyScaffold and setuptools.

A simple a PyScaffold + |pip-tools|_ workflow looks like:

.. code-block:: bash

    $ putup myproj --venv --venv-install pip-tools setuptools_scm && cd myproj
    $ source .venv/bin/activate
    # ... edit setup.cfg to add dependencies ...
    $ echo '-e file:.' > requirements.in
    $ echo -e 'tox\nsphinx\nptpython' >> requirements.in  # etc
    $ pip-compile
    $ pip-sync
    $ tox
    # ... do some debugging/live experimentation running Python in the terminal
    $ ptpython
    $ git add *requirements.{in,txt}

.. TODO: Remove the manual installation/update of pip, setuptools and setuptools_scm
   once pip starts supporting editable installs with pyproject.toml

After adding dependencies in ``setup.cfg`` (or to ``requirements.in``),
you can run ``pip-compile && pip-sync`` to add them to your virtual environment.
If you want to add a dependency to the dev environment only, you can also:

.. code-block:: bash

    $ echo "mydep>=1.2,<=2" >> requirements.in && pip-compile && pip-sync

.. warning::

    *Experimental Feature* - the methods described here for integrating |pip-tools|_
    and PyScaffold in a single workflow are tested to a certain degree and not
    considered stable.
    The usage of relative paths in the compiled ``requirements.txt`` file is a
    feature that have being several years in the making and still is under
    discussion. As everything in Python's packaging ecosystem right now,
    the implementation, APIs and specs might change in the future so it is up to
    the user to keep an eye on the official docs and use the logic explained
    here to achieve the expected results with the most up-to-date API
    |pip-tools|_ have to offer.

    The issue https://github.com/jazzband/pip-tools/issues/204 is worth
    following.

    If you find that the procedure here no longer works, please open an issue
    on https://github.com/pyscaffold/pyscaffold/issues.

.. |pip-tools| replace:: ``pip-tools``
.. _pip-tools: https://github.com/jazzband/pip-tools
