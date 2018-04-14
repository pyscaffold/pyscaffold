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

.. image:: http://pyscaffold.org/en/latest/_images/logo.png
    :height: 512px
    :width: 512px
    :scale: 60 %
    :alt: PyScaffold logo
    :align: center

|

PyScaffold helps you setup a new Python project. It is as easy as::

    putup my_project

This will create a new folder called ``my_project`` containing a perfect *project
template* with everything you need for some serious coding. After the usual::

   python setup.py develop

you are all set and ready to go.

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have Git_ installed and set up on your PC,
meaning at least your name and email are configured.
The project template in ``my_project`` provides you with following features:


Configuration & Packaging
=========================

All configuration can be done in ``setup.cfg`` like changing the description,
url, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.

In order to build a source, binary or wheel distribution, just run
``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel``.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that reside within your package and
are tracked by Git will automatically be included
(``include_package_data = True`` in ``setup.cfg``).
It is not necessary to have a ``MANIFEST.in`` file for this to work.

Complete Git Integration
========================

Your project is an already initialised Git repository and ``setup.py`` uses
the information of tags to infer the version of your project with the help of
setuptools_scm_.
To use this feature, you need to tag with the format ``MAJOR.MINOR[.PATCH]``
, e.g. ``0.0.1`` or ``0.1``.
Run ``python setup.py --version`` to retrieve the current PEP440_-compliant
version. This version
will be used when building a package and is also accessible through
``my_project.__version__``.

Unleash the power of Git by using its `pre-commit hooks`_. This feature is
available through the ``--pre-commit`` flag. After your project's scaffold
was generated, make sure pre-commit is installed, e.g. ``pip install pre-commit``,
then just run ``pre-commit install``.

A default ``.gitignore`` file is also provided; it is
well adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

Build the documentation with ``python setup.py docs`` and run doctests with
``python setup.py doctest`` after you have `Sphinx`_ installed.
Start editing the file ``docs/index.rst`` to extend the documentation.
The documentation also works with `Read the Docs`_.

The `Numpy and Google style docstrings`_ are activated by default.
Just make sure Sphinx 1.3 or above is installed.


Unittest & Coverage
===================

Run ``python setup.py test`` to run all unittests defined in the subfolder
``tests`` with the help of `py.test`_ and pytest-runner_. Some sane
default flags for py.test are already defined in the ``[tool:pytest]`` section of
``setup.cfg``. The py.test plugin `pytest-cov`_ is used to automatically
generate a coverage report. It is also possible to provide additional
parameters and flags on the commandline, e.g., type::

    python setup.py test --addopts -h

to show the help of py.test.

.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--travis`` to generate
templates of the `Travis`_ configuration files
``.travis.yml`` and ``tests/travis_install.sh`` which even features the
coverage and stats system `Coveralls`_.
In order to use the virtualenv management and test tool `Tox`_ the flag
``--tox`` can be specified.


Management of Requirements & Licenses
=====================================

Installation requirements of your project can be defined inside ``setup.cfg``,
e.g. ``install_requires = numpy; scipy``. To avoid package dependency problems,
it is common to not pin installation requirements to any specific version,
although minimum versions, e.g. ``sphinx>=1.3``, or maximum versions, e.g.
``pandas<0.12``, are used sometimes.

More specific installation requirements should go into ``requirements.txt``.
This file can also be managed with the help of ``pip compile`` from `pip-tools`_
that basically pins packages to the current version, e.g. ``numpy==1.13.1``.
The packages defined in ``requirements.txt`` can be easily installed with::

    pip install -r requirements.txt

All licenses from `choosealicense.com`_ can be easily selected with the help
of the ``--license`` flag.


Extensions
==========

PyScaffold comes with several extensions:

* Create a `Django project`_ with the flag ``--django`` which is equivalent to
  ``django-admin.py startproject my_project`` enhanced by PyScaffold's features.


* With the help of `Cookiecutter`_ it is possible to further customize your project
  setup with a template tailored for PyScaffold. Just use the flag ``--cookiecutter TEMPLATE``
  to use a cookiecutter template which will be refined by PyScaffold afterwards.

* ... and many more like ``--gitlab`` to create the necessary files for GitLab_.

Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putup --update my_project`` when a new version of PyScaffold was released.
An update will only overwrite files that are not often altered by users like
``setup.py``. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!


.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _setuptools_scm: https://pypi.python.org/pypi/setuptools_scm/
.. _Git: http://git-scm.com/
.. _PEP440: http://www.python.org/dev/peps/pep-0440/
.. _pre-commit hooks: http://pre-commit.com/
.. _py.test: http://pytest.org/
.. _Sphinx: http://www.sphinx-doc.org/
.. _Read the Docs: https://readthedocs.org/
.. _Numpy and Google style docstrings: http://sphinx-doc.org/latest/ext/napoleon.html
.. _pytest-runner: https://pypi.python.org/pypi/pytest-runner
.. _pytest-cov: https://github.com/schlamar/pytest-cov
.. _Travis: https://travis-ci.org
.. _Coveralls: https://coveralls.io/
.. _Tox: https://tox.readthedocs.org/
.. _choosealicense.com: http://choosealicense.com/
.. _Django project: https://www.djangoproject.com/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
.. _GitLab: https://about.gitlab.com/
.. _pip-tools: https://github.com/jazzband/pip-tools/
