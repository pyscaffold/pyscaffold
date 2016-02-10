.. _features:

========
Features
========

PyScaffold comes with a lot of elaborated features and configuration defaults
to make the most common tasks in developing, maintaining and distributing your
own Python package as easy as possible.


Configuration & Packaging
=========================

All configuration can be done in ``setup.cfg`` like changing the description,
url, classifiers and even console scripts of your project with the help of
`pbr <http://docs.openstack.org/developer/pbr/>`_. That means in most
cases it is not necessary to tamper with ``setup.py``. The syntax of
``setup.cfg`` is pretty much self-explanatory and well commented, check out
this  :ref:`example <configuration>` or `pbr's usage manual
<http://docs.openstack.org/developer/pbr/#usage>`_.

In order to build a source, binary or wheel distribution, just run
``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel``.

.. rubric:: Namespace Packages

Optionally, `namespace packages <http://pythonhosted.org/setuptools/setuptools.html#namespace-packages>`_
can be used, if you are planning to distribute a larger package as a collection
of smaller ones. For example, use::

    putup my_project --package my_package --with-namespace com.my_domain

to define ``my_package`` inside the namespace ``com.my_domain`` in java-style.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, inside your package can be
configured under the ``[files]`` section in ``setup.cfg``. It is not necessary
to have a ``MANIFEST.in`` file for this to work.
To read this data in your code, use::

    from pkgutil import get_data
    data = get_data('my_package', 'path/to/my/data.txt')

.. note::

    Make sure that all files you specify in ``[files]`` have been added to
    the repository!

Complete Git Integration
========================

Your project is already an initialised Git repository and ``setup.py`` uses
the information of tags to infer the version of your project with the help of
`setuptools_scm <https://pypi.python.org/pypi/setuptools_scm/>`_.
To use this feature you need to tag with the format ``MAJOR.MINOR[.PATCH]``
, e.g. ``0.0.1`` or ``0.1``.
Run ``python setup.py --version`` to retrieve the current `PEP440
<http://www.python.org/dev/peps/pep-0440/>`_-compliant version. This version
will be used when building a package and is also accessible through
``my_project.__version__``.

Unleash the power of Git by using its `pre-commit hooks
<http://pre-commit.com/>`_. This feature is available through the
``--with-pre-commit`` flag. After your project's scaffold was generated, make
sure pre-commit is installed, e.g. ``pip install pre-commit``, then just run
``pre-commit install``.

It goes unsaid that also a default ``.gitignore`` file is provided that is well
adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

Build the documentation with ``python setup.py docs`` and run doctests with
``python setup.py doctest``. Start editing the file ``docs/index.rst`` to
extend the documentation. The documentation also works with `Read the Docs
<https://readthedocs.org/>`_.

The `Numpy and Google style docstrings
<http://sphinx-doc.org/latest/ext/napoleon.html>`_ are activated by default.
Just make sure Sphinx 1.3 or above is installed.


Unittest & Coverage
===================

Run ``python setup.py test`` to run all unittests defined in the subfolder
``tests`` with the help of `py.test <http://pytest.org/>`_ and
`pytest-runner <https://pypi.python.org/pypi/pytest-runner>`_. Some sane
default flags for py.test are already defined in the ``[pytest]`` section of
``setup.cfg``. The py.test plugin
`pytest-cov <https://github.com/schlamar/pytest-cov>`_ is used to automatically
generate a coverage report. It is also possible to provide additional
parameters and flags on the commandline, e.g., type::

    python setup.py test --addopts -h

to show the help of py.test.

.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--with-travis`` to generate
templates of the `Travis <https://travis-ci.org/>`_ configuration files
``.travis.yml`` and ``tests/travis_install.sh`` which even features the
coverage and stats system `Coveralls <https://coveralls.io/>`_.
In order to use the virtualenv management and test tool `Tox
<https://tox.readthedocs.org/>`_ the flag ``--with-tox`` can be specified.

.. rubric:: Managing test environments with tox

Run ``tox`` to generate test virtual environments for various python
environments defined in the generated :file:`tox.ini`. Testing and building
*sdists* for python 2.7 and python 3.4 is just as simple with tox as::

        tox -e py27,py34

Environments for tests with the the static code analyzers pyflakes and pep8
which are bundled in `flake8 <http://flake8.readthedocs.org/>`_ are included
as well. Run it explicitly with::

        tox -e flake8

With tox, you can use the ``--recreate`` flag to force tox to create new
environments. By default, PyScaffold's tox configuration will execute tests for
a variety of python versions. If an environment is not available on the system
the tests are skipped gracefully. You can relay on the `tox documentation
<http://tox.readthedocs.org/en/latest/>`_ for detailed configuration options.


Management of Requirements & Licenses
=====================================

Add the requirements of your project to ``requirements.txt`` and
``test-requirements.txt`` which will be automatically used by ``setup.py``.
This also allows you to easily customize a plain virtual environment with::

    pip install -r requirements.txt -r test-requirements.txt

Only absolutely necessary requirements of your project shoulbe be stated in
``requirements.txt`` while the requirements only used for development and
especially for running the unittests should go into ``test-requirements.txt``.

Since PyScaffold uses pbr it is also possible to define `requirements depending
on your Python version
<http://docs.openstack.org/developer/pbr/#requirements>`_. Use the environment
variable ``PBR_REQUIREMENTS_FILES`` to define a comma-separated list of
requirement files if you want to use non-default names and locations.

All licenses from `choosealicense.com <http://choosealicense.com/>`_ can be
easily selected with the help of the ``--license`` flag.


Django & Cookiecutter
=====================

Create a `Django project <https://www.djangoproject.com/>`_ with the flag
``--with-django`` which is equivalent to
``django-admin.py startproject my_project`` enhanced by PyScaffold's features.

With the help of `Cookiecutter <https://cookiecutter.readthedocs.org/>`_ it
is possible to customize your project setup. Just use the flag
``--with-cookiecutter TEMPLATE`` to use a cookiecutter template which will be
refined by PyScaffold afterwards.


Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putput --update my_project`` when a new version of PyScaffold was released.
An update will only overwrite files that are not often altered by users like
setup.py. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!
Also check out if :ref:`configuration options <configuration>` in
``setup.cfg`` have changed.

.. note::

    If you are updating from a PyScaffold version before 2.0, you must
    manually remove the files ``versioneer.py`` and ``MANIFEST.in``. If you
    are updating from a version prior to 2.2, you must remove
    ``${PACKAGE}/_version.py``.
