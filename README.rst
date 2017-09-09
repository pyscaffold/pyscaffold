.. image:: https://travis-ci.org/blue-yonder/pyscaffold.svg?branch=master
    :target: https://travis-ci.org/blue-yonder/pyscaffold
.. image:: https://coveralls.io/repos/blue-yonder/pyscaffold/badge.png
    :target: https://coveralls.io/r/blue-yonder/pyscaffold
.. image:: https://requires.io/github/blue-yonder/pyscaffold/requirements.png?branch=master
    :target: https://requires.io/github/blue-yonder/pyscaffold/requirements/?branch=master
    :alt: Requirements Status
.. image:: https://badges.gitter.im/Join%20Chat.svg
    :alt: Join the chat at https://gitter.im/blue-yonder/pyscaffold
    :target: https://gitter.im/blue-yonder/pyscaffold?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

|

.. image:: http://pyscaffold.readthedocs.org/en/latest/_images/logo.png
    :height: 512px
    :width: 512px
    :scale: 60 %
    :alt: PyScaffold logo
    :align: center

|

PyScaffold helps you to easily setup a new Python project, it is as easy as::

    putup my_project

This will create a new folder ``my_project`` containing a perfect *project
template* with everything you need for some serious coding.

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have `Git  <http://git-scm.com/>`_ installed and set up on your PC,
meaning at least your name and email configured.
The project template in ``my_project`` provides you with following features:


Configuration & Packaging
=========================

All configuration can be done in ``setup.cfg`` like changing the description,
url, classifiers and even console scripts of your project. That means in most
cases it is not necessary to tamper with ``setup.py``.

In order to build a source, binary or wheel distribution, just run
``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel``.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, inside your package can be
configured under the ``[files]`` section in ``setup.cfg``. It is not necessary
to have a ``MANIFEST.in`` file for this to work.

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
default flags for py.test are already defined in the ``[tool:pytest]`` section of
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
If you prefer to use `GitLab-CI <https://gitlab.com>`_ then you can use the flag
``--with-gitlab-ci`` to get a ``.gitlab-ci.yml`` configuration.


Management of Requirements & Licenses
=====================================

Add the requirements of your project to ``requirements.txt`` and
``test-requirements.txt`` which will be automatically used by ``setup.py``.
This also allows you to easily customize a plain virtual environment with::

    pip install -r requirements.txt -r test-requirements.txt

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
