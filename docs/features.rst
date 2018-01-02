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
url, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.
The syntax of ``setup.cfg`` is pretty much self-explanatory and well commented,
check out this :ref:`example <configuration>` or `setuptools' documentation`_.

In order to build a source, binary or wheel distribution, just run
``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel``.

.. rubric:: Namespace Packages

Optionally, `namespace packages`_ can be used, if you are planning to distribute
a larger package as a collection of smaller ones. For example, use::

    putup my_project --package my_package --namespace com.my_domain

to define ``my_package`` inside the namespace ``com.my_domain`` in java-style.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that reside within your package
will automatically be included (``include_package_data = True`` in ``setup.cfg``).
It is not necessary to have a ``MANIFEST.in`` file for this to work. Just make
sure that all files are added to your repository.
To read this data in your code, use::

    from pkgutil import get_data
    data = get_data('my_package', 'path/to/my/data.txt')


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
``--pre-commit`` flag. After your project's scaffold was generated, make
sure pre-commit is installed, e.g. ``pip install pre-commit``, then just run
``pre-commit install``.

It goes unsaid that also a default ``.gitignore`` file is provided that is well
adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

Build the documentation with ``python setup.py docs`` and run doctests with
``python setup.py doctest``. Start editing the file ``docs/index.rst`` to
extend the documentation. The documentation also works with `Read the Docs`_.

The `Numpy and Google style docstrings`_ are activated by default.
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
can be activated in ``setup.cfg``. Use the flag ``--travis`` to generate
templates of the `Travis <https://travis-ci.org/>`_ configuration files
``.travis.yml`` and ``tests/travis_install.sh`` which even features the
coverage and stats system `Coveralls <https://coveralls.io/>`_.
In order to use the virtualenv management and test tool `Tox
<https://tox.readthedocs.org/>`_ the flag ``--tox`` can be specified.
If you are using `GitLab <https://gitlab.com/>`_ you can get a default 
`.gitlab-ci.yml` also running `pytest-cov` with the flag ``--gitlab``.

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
the tests are skipped gracefully. You can rely on the `tox documentation`_
for detailed configuration options.


Management of Requirements & Licenses
=====================================

Installation requirements of your project can be defined inside ``setup.cfg``,
e.g. ``install_requires = numpy; scipy``. To avoid package dependency problems
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

There is also documentation about :ref:`writing extensions <extensions>`.

Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putput --update my_project`` when a new version of PyScaffold was released.
An update will only overwrite files that are not often altered by users like
``setup.py``. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!
Also check out if :ref:`configuration options <configuration>` in
``setup.cfg`` have changed.


Updates from PyScaffold 2
-------------------------

Since the overall structure of a project set up with PyScaffold 2 differs quite
much from a project generated with PyScaffold 3 it is not possible to just use
the ``--update`` parameter. Still with some manual efforts an update from
a scaffold generated with PyScaffold 2 to PyScaffold 3's scaffold is quite easy.
Assume the name of our project is ``old_project`` with a package called
``old_package`` and no namespaces then just:

1) make sure your worktree is not dirty, i.e. commit all your changes,
2) run ``putup old_project --force --no-skeleton -p old_package`` to generate
   the new structure inplace and ``cd`` into your project,
3) move with ``git mv old_package/* src/old_package/ --force`` your old package
   over to the new ``src`` directory,
4) check ``git status`` and add untracked files from the new structure,
5) use ``git difftool`` to check all overwritten files, especially ``setup.cfg``,
   and transfer custom configurations from the old structure to the new,
6) check if ``python setup.py test sdist`` works and commit your changes.

Adding features
---------------

With the help of an experimental updating functionality it is also possible to
add additional features to your existing project scaffold. If a scaffold lacking
``.travis.yml`` was created with ``putup my_project`` it can later be added by issuing
``putup --update my_project --travis``. For this to work, PyScaffold stores all
options that were initially used to put up the scaffold under the ``[pysaffold]``
section in ``setup.cfg``. Be aware that right now PyScaffold provides no way to
remove a feature which was once added.


.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html
.. _setuptools' documentation: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _namespace packages: http://pythonhosted.org/setuptools/setuptools.html#namespace-packages
.. _Read the Docs: https://readthedocs.org/
.. _tox documentation: http://tox.readthedocs.org/en/latest/
.. _Numpy and Google style docstrings: http://sphinx-doc.org/latest/ext/napoleon.html
.. _choosealicense.com: http://choosealicense.com/
.. _Django project: https://www.djangoproject.com/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
.. _pip-tools: https://github.com/jazzband/pip-tools/
