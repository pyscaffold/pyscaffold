.. _dependencies:

=====================
Dependency Management
=====================

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

.. _Donald Stufft: https://caremad.io/posts/2013/07/setup-vs-requirement/).
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
    $ putup myproj --tox
    $ cd myproj
    $ python -m venv .venv
    $ source .venv/bin/activate
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

TODO

How to integrate ``pip-tools``
------------------------------

TODO
