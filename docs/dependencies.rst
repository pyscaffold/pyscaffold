.. _dependencies:

=====================
Dependency Management
=====================

.. warning::

    *Experimental Feature* - PyScaffold support for virtual environment
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

If you use |pytest-runner|_ adding a ``--extras`` flag will do the trick of
making sure these dependencies are installed, and if you use ``tox``, the same
is accomplished with |extras|_. By default PyScaffold will take care of these
configurations for you.

.. note:: If you prefer to use just ``tox`` and keep everything inside
    ``tox.ini``, please go ahead and move your test dependencies.
    Every should work just fine :)

.. warning:: PyScaffold strongly advocates the use of test runners to guarantee
    your project is correctly packaged/works in isolated environments.
    A good start is to create a new project passing the ``--tox`` option to
    ``putup`` and try running ``tox`` in your project root.

.. |pytest-runner| replace:: ``pytest-runner``
.. _pytest-runner: https://github.com/pytest-dev/pytest-runner
.. |extras| replace:: the ``extras`` configuration field
.. _extras: http://tox.readthedocs.io/en/latest/config.html#confval-extras=MULTI-LINE-LIST


Development Environment
=======================

As previously mentioned, PyScaffold will get you covered when specifying the
**abstract** or test dependencies of your package. We provide sensible
configurations for ``setuptools``, ``tox`` and ``pytest-runner``
out-of-the-box. In most of the cases this is enough, since developers in the
Python community are used to rely on tools like |virtualenv|_ and have a
workflow that take advantage of such configurations. As an example, someone
could do:

.. code-block:: bash

    $ pip install pyscaffold
    $ putup myproj --tox
    $ cd myproj
    $ python -m venv .venv
    $ source .venv/bin/activate
    # ... edit setup.cfg to add dependencies ...
    $ pip install -e .
    $ pip install tox
    $ tox

However, someone could argue that this process is pretty manual and laborious
to maintain specially when the developer changes the **abstract** dependencies.
Moreover, it is desirable to keep track of the version of each item in the
dependency graph, so the developer can have environment reproducibility when
trying to use another machine or discuss bugs with colleagues.

In the following sections, we describe how to use two popular command line
tools, supported by PyScaffold, to tackle these issues.

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
while the dev set should contain things like ``tox``, ``pytest-runner``,
``sphinx``, ``pre-commit``, ``ptpython`` or any other tool the developer uses
while developing.

.. note:: Test dependencies are internally managed by the test runner,
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
    $ putup myproj --tox
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

.. _Pipenv: https://docs.pipenv.org/


..
    TODO: As reported in issue https://github.com/jazzband/pip-tools/issues/663,
    pip-tools is generating absolute file paths inside ``requirements.txt``
    for ``-e .``, which prevents adding concrete dependencies to the repository
    and therefore misses the whole point of using such tool.
    We need to monitor the issue and them update and uncomment the following
    text:

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
    ``setup.cfg``' ``install_requires`` is to add ``-e .`` to it. For the dev
    environment, one could create a ``dev-requirements.in`` file with all the
    packages that help during the development.

    Basically, a PyScaffold+``pip-tools`` workflow looks like:

    .. code-block:: bash

        $ pip install pyscaffold pip-tools
        $ putup myproj --tox
        $ cd myproj
        $ python -m venv .venv
        $ source .venv/bin/activate
        # ... edit setup.cfg to add dependencies ...
        $ echo '-e .' > requirements.in
        $ echo -e 'tox\nsphinx\nptpython' > requirements.in  # etc
        $ ls -1 *.in | sed 'p;s/\(.*\)requirements\.in$/-o \1requirements.txt/g' \
          | xargs -L2 -- pip-compile
        $ pip-compile dev-requirements.in -o dev-requirements.txt
        $ pip-sync *requirements.txt
        $ tox
        $ git add *requirements.{in,txt}

    After adding dependencies in ``setup.cfg`` (or to ``dev-requirements.in``),
    you can run ``pip-compile ... && pip-sync *requirements.txt``
    to add them to your virtual environment.

    .. |pip-tools| replace:: ``pip-tools``
    .. _pip-tools: https://github.com/jazzband/pip-tools
