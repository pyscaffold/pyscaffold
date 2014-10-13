.. _features:

========
Features
========

Packaging
=========

Run ``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel`` to build a source, binary or wheel
distribution.


Complete Git Integration
========================

Your project is already an initialised Git repository and ``setup.py`` uses
the information of tags to infer the version of your project with the help of
`versioneer <https://github.com/warner/python-versioneer>`_.
To use this feature you need to tag with the format ``vMAJOR.MINOR[.REVISION]``
, e.g. ``v0.0.1`` or ``v0.1``. The prefix ``v`` is needed!
Run ``python setup.py version`` to retrieve the current `PEP440
<http://www.python.org/dev/peps/pep-0440/>`_-compliant version. This version
will be used when building a package and is also accessible through
``my_project.__version__``.
The version will be ``unknown`` until you have added a first tag.

Unleash the power of Git by using its `pre-commit hooks
<http://pre-commit.com/>`_. This feature is available through the
``--with-pre-commit`` flag. After your project's scaffold was generated, make
sure pre-commit is installed, e.g. ``pip install pre-commit``, then just run
``pre-commit install``.


Sphinx Documentation
====================

Build the documentation with ``python setup.py docs`` and run doctests with
``python setup.py doctest``. Start editing the file ``docs/index.rst`` to
extend the documentation. The documentation also works with `Read the Docs
<https://readthedocs.org/>`_.


Unittest & Coverage
===================

Run ``python setup.py test`` to run all unittests defined in the subfolder
``tests`` with the help of `py.test <http://pytest.org/>`_. The py.test plugin
`pytest-cov <https://github.com/schlamar/pytest-cov>`_ is used to automatically
generate a coverage report. For usage with a continuous integration software
JUnit and Coverage XML output can be activated. Checkout ``putup -h`` for
details. Use the flag ``--with-travis`` to generate templates of the
`Travis <https://travis-ci.org/>`_ configuration files ``.travis.yml`` and
``tests/travis_install.sh`` which even features the coverage and stats system
`Coveralls <https://coveralls.io/>`_.

.. rubric:: Managing test environments with tox

Run ``tox`` to generate test virtual environments for various python
environments defined in the generated :file:`tox.ini`. Testing and building
*sdists* for python 2.7 and python 3.4 is just as simple with tox as::

        tox -e py27,py34

Environments for tests with the the static code analyzers pyflakes and pep8 are
included as optional test environments::

        tox -e flake,pep8

With tox, you can use the ``--recreate`` flag to force tox to create new
virtualenvs. By default, pyscaffold's tox configuration will execute tests for
a variety of python versions. If an environment is not available on the system
the tests are skipped gracefully. You can relay on the `tox documentation
<http://tox.readthedocs.org/en/latest/>`_ for detialed configuration options.


Requirements Management
=======================

Add the requirements of your project to the ``requirements.txt`` file which
will be automatically used by ``setup.py``.


Licenses
========

All licenses from `choosealicense.com <http://choosealicense.com/>`_ can be
easily selected with the help of the ``--license`` flag.


Django
======

Create a `Django project <https://www.djangoproject.com/>`_ with the flag
``--with-django`` which is equivalent to
``django-admin.py startproject my_project`` enhanced by PyScaffold's features.


Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putput --update my_project`` when a new version of PyScaffold was released.
It may also be used to change the url, license and description setting.
An update will only overwrite files that are not often altered by users like
setup.py, versioneer.py etc. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely save to use
since the git repository of the existing project is not touched!
