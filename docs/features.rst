.. _features:

========
Features
========

PyScaffold comes with a lot of elaborated features and configuration defaults
to make the most common tasks in developing, maintaining and distributing your
own Python package as easy as possible.


Configuration, Packaging & Distribution
=======================================

All configuration can be done in ``setup.cfg`` like changing the description,
URL, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.
The syntax of ``setup.cfg`` is pretty much self-explanatory and well commented,
check out this :ref:`example <configuration>` or `setuptools' documentation`_.

If you use tox_, PyScaffold will already configure everything out of the box
[#feat1]_ so you can easily build your distribution, in a `PEP 517`_/`PEP 518`_
compliant way, by just running::

    tox -e build

Alternatively, if you are not a huge fan of isolated builds, or prefer running
the commands yourself, you can execute ``python setup.py sdist`` or
``python setup.py bdist_wheel`` (recommended).

.. rubric:: Uploading to PyPI

Of course uploading your package to the official Python package index PyPI_
for distribution also works out of the box. Just create a distribution as
mentioned above and use tox_ to publish with::

    tox -e publish

This will first upload your package `using TestPyPI`_, so you can be a good
citizen of the Python world, check/test everything is fine, and then, when you
are absolutely sure the moment has come for your package to shine, you can go
ahead and run ``tox -e --publish -- --repository pypi`` [#feat2]_. Just
remember that for this to work, you have to first register a PyPI_ account (and
also a TestPyPI_ one).

Under the hood, tox_ uses twine_ for uploads to PyPI_ (as configured by
PyScaffold in the ``tox.ini`` file), so if you prefer running things yourself,
you can also do::

    pip install twine
    twine upload --repository testpypi dist/*

Please notice that PyPI_ does not allow uploading local versions, e.g. ``0.0.dev5+gc5da6ad``,
for practical reasons. Thus, you have to create a git tag before uploading a version
of your distribution. Read more about it in the versioning_ section below.

.. warning::
   Old guides might mention ``python setup.py upload``, but its use is strongly discouraged
   nowadays and even some of the new PyPI_ features won't work correctly if you don't use twine_.

.. rubric:: Namespace Packages

If you want to work with `namespace packages`_, you will be glad to hear that
PyScaffold supports the `PEP 420`_ specification for implicit namespaces,
which is very useful to distribute a larger package as a collection of smaller ones.
``putup`` can automatically setup everything you need with the ``--namespace``
option. For example, use::

    putup my_project --package my_package --namespace com.my_domain

to define ``my_package`` inside the namespace ``com.my_domain``, Java-style.

.. note::
   Prior to PyScaffold 4.0, namespaces were generated
   explicitly with `pkg_resources`_, instead of  `PEP 420`_. Moreover, if you
   are developing "subpackages" for already existing namespaces, please check
   which convention the namespaces are currently following. Different styles of
   `namespace packages`_ might be incompatible. If you don't want to update
   existing namespace packages to `PEP 420`_, you will probably need to
   manually copy the ``__init__.py`` file for the umbrella namespace folder
   from an existing project. Additionally have a look in our :ref:`FAQ <faq>`
   about how to disable implicit namespaces.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that **must reside within** your package, e.g.
under ``my_project/src/my_package``, and are tracked by Git will automatically be included
if ``include_package_data = True`` in ``setup.cfg``.
It is not necessary to have a ``MANIFEST.in`` file for this to work. Just make
sure that all files are added to your repository.
To read this data in your code, use::

    from pkgutil import get_data
    data = get_data('my_package', 'path/to/my/data.txt')

Starting from Python 3.7 an even better approach is using `importlib.resources`_::

    from importlib.resources import read_text, read_binary
    data = read_text('my_package.sub_package', 'data.txt')

Note that we need a proper package structure in this case, i.e. directories need
to contain ``__init__.py`` and we only specify the file ``data.txt``, no path is allowed.
The library importlib_resources_ provides a backport of this feature.

Please have in mind that the ``include_package_data`` option in ``setup.cfg`` is only
guaranteed to be read when creating a `wheels`_ distribution. Other distribution methods might
behave unexpectedly (e.g. always including data files even when
``include_package_data = False``). Therefore, the best option if you want to have
data files in your repository **but not as part of the pip installable package**
is to add them somewhere **outside** the ``src`` directory (e.g. a ``files``
directory in the root of the project, or inside ``tests`` if you use them for
checks). Additionally you can exclude them explicitly via the
``[options.packages.find] exclude`` option in ``setup.cfg``.

.. tip::
   Using package files to store runtime configuration or mutable data is not
   considered good practice. Package files should be read-only. If you need
   configuration files, or files that should be written at runtime, please
   consider doing so inside standard locations in the user's home folder
   (`appdirs`_ is a good library for that).
   If needed you can even create them at the first usage from a read-only
   template, which in turn can be a package file.


.. _versioning:

Versioning and Git Integration
==============================

Your project is already an initialised Git repository and setuptools_ uses the
information of tags to infer the version of your project with the help of
`setuptools_scm`_.  To use this feature you need to tag with the format
``MAJOR.MINOR[.PATCH]`` , e.g. ``0.0.1`` or ``0.1``.
Run ``python setup.py --version`` to retrieve the current `PEP 440`_-compliant version.
This version will be used when building a package and is also accessible through
``my_project.__version__``. If you want to upload to PyPI_ you have to tag the current commit
before uploading since PyPI_ does not allow local versions, e.g. ``0.0.dev5+gc5da6ad``,
for practical reasons.

Please check our docs for the :ref:`best practices and common errors with version
numbers <version-faq>`.


.. rubric:: Pre-commit Hooks

Unleash the power of Git by using its `pre-commit hooks`_.
This feature is available through the  ``--pre-commit`` flag.
After your project's scaffold was generated, make sure pre-commit is
installed, e.g. ``pip install pre-commit``, then just run ``pre-commit install``.

It goes unsaid that also a default ``.gitignore`` file is provided that is well
adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

PyScaffold will prepare a ``docs`` directory with all you need to start writing
your documentation. Start editing the file ``docs/index.rst`` to extend the documentation
and note that even the `Numpy and Google style docstrings`_ are activated by default.

If you have `tox`_ in your system, simply run ``tox -e docs`` or ``tox -e
doctests`` to compile the docs or run the doctests.

Alternatively, if you have `make`_ and `Sphinx`_ installed in your computer, build the
documentation with ``make -C docs html`` and run doctests with
``make -C docs doctest``. Just make sure Sphinx 1.3 or above is installed.

The documentation also works with `Read the Docs`_. Please check the `RTD
guides`_ to learn how to import your documents into the website.

.. note::
   In order to generate the docs locally, you will need to install any
   dependency used to build your doc files (and probably all your project dependencies) in
   the same Python environment where Sphinx_ is installed (either the global Python
   installation or a conda/virtualenv/venv environment).
   For example, if you want to use the `Read the Docs`_ classic theme,
   the ``sphinx_rtd_theme`` package should be installed.

   If you are using ``tox -e docs``, tox_ will take care of generating a
   virtual environment and installing all these dependencies automatically.
   You will only need to list your doc dependencies (like ``sphinx_rtd_theme``)
   under the ``deps`` property of the ``[testenv:{docs,doctests}]`` section
   in the ``tox.ini`` file.
   Your can also use the ``docs/requirements.txt`` file to store them.
   This file can be used by both `Read the Docs`_ and tox_
   when generating the docs.


Dependency Management in a Breeze
=================================

PyScaffold out of the box allows developers to express abstract dependencies
and take advantage of ``pip`` to manage installation. It also can be used
together with a `virtual environment`_ (also called *virtual env*)
to avoid `dependency hell`_ during both development and production stages.

If you like the traditional style of dependency management using a virtual env
co-located with your package, PyScaffold can help to reduce the boilerplate.
With the ``--venv`` option, a virtualenv will be bootstrapped and waiting to be
activated. And if you are the kind of person that always install the same
packages when creating a virtual env, PyScaffold's option ``--venv-install
PACKAGE`` will be the right one for you. You can even integrate `pip-tools`_ in
this workflow, by putting a ``-e file:.`` in your *requirements.in*.

Alternatively, PyPA's `Pipenv`_ can be integrated in any PyScaffold-generated
project by following standard `setuptools`_ conventions.  Keeping abstract
requirements in ``setup.cfg`` and running ``pipenv install -e .`` is basically
what you have to do.

You can check the details on how all of that works in
:ref:`Dependency Management <dependencies>`.

.. warning::

    *Experimental Feature* - Pipenv and pip-tools support is experimental and might
    change in the future.


Automation, Tests & Coverage
============================

PyScaffold relies on pytest_ to run all automated tests defined in the subfolder
``tests``.  Some sane default flags for pytest are already defined in the
``[tool:pytest]`` section of ``setup.cfg``. The pytest plugin `pytest-cov`_ is used
to automatically generate a coverage report. It is also possible to provide
additional parameters and flags on the commandline, e.g., type::

    pytest -h

to show the help of pytest (requires `pytest`_ to be installed in your system
or `virtual environment`_).

.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--cirrus`` to generate
templates of the `Cirrus CI`_ configuration file
``.cirrus.yml`` which even features the coverage and stats system `Coveralls`_.
If you are using `GitLab`_ you can get a default
`.gitlab-ci.yml` also running `pytest-cov` with the flag ``--gitlab``.

.. rubric:: Managing test environments and tasks with tox

Projects generated with PyScaffold are configured by default to use `tox`_ to
run some common tasks. Tox is a `virtual environment`_ management and test tool that allows
you to define and run custom tasks that call executables from Python packages.

If you simply install `tox`_ and run from the root folder of your project::

    tox

`tox`_ will download the dependencies you have specified, build the
package, install it in a virtual environment and run the tests using `pytest`_, so you
are sure everything is properly tested. You can rely on the `tox documentation`_
for detailed configuration options (which include the possibility of running
the tests for different versions of Python).

You are not limited to running your tests, with `tox`_ you can define all sorts
of automation tasks. Here are a few examples for you::

    tox -e build  # will bundle your package and create a distribution inside the `dist` folder
    tox -e publish  # will upload your distribution to a package index server
    tox -e docs  # will build your docs

but you can go ahead and check `tox examples`_, or this `tox tutorial`_ from
Sean Hammond for more ideas, e.g.  running static code analyzers (pyflakes and
pep8) with `flake8`_. Run ``tox -av`` to list all the available tasks.


Management of Requirements & Licenses
=====================================

Installation requirements of your project can be defined inside ``setup.cfg``,
e.g. ``install_requires = numpy; scipy``. To avoid package dependency problems
it is common to not pin installation requirements to any specific version,
although minimum versions, e.g. ``sphinx>=1.3``, and/or maximum versions, e.g.
``pandas<0.12``, are used frequently in accordance with `semantic versioning`_.

For test/dev purposes, you can additionally create a ``requirements.txt``
pinning packages to specific version, e.g. ``numpy==1.13.1``.
This helps to ensure reproducibility, but be sure to read our
:ref:`Dependency Management Guide <dependencies>` to understand the role of a
``requirements.txt`` file for library and application projects
(``pip-compile`` from `pip-tools`_ can help you to manage that file).
Packages defined in ``requirements.txt`` can be easily installed with::

    pip install -r requirements.txt

The most popular open source licenses can be easily added to your project with
the help of the ``--license`` flag. You only need to specify the license identifier
according to the `SPDX index`_ so PyScaffold can generate the appropriate
``LICENSE.txt`` and configure your package. For example::

    putup --license MPL-2.0 my_project

will create the ``my_project`` package under the `Mozilla Public License 2.0`_
The available licenses can be listed with ``putup --help``, and you can find
more information about each license in the `SPDX index`_ and `choosealicense.com`_.


Extensions
==========

PyScaffold offers several extensions:

* If you want a project setup for a *Data Science* task, just use ``--dsproject``
  after having installed `pyscaffoldext-dsproject`_.

* Have a ``README.md`` based on Markdown instead of ``README.rst`` by using
  ``--markdown`` after having installed `pyscaffoldext-markdown`_.

* Create a `Django project`_ with the flag ``--django`` which is equivalent to
  ``django-admin startproject my_project`` enhanced by PyScaffold's features
  (requires `pyscaffoldext-django`_).

* … and many more like ``--gitlab`` to create the necessary files for GitLab_,
  ``--travis`` for TravisCI_, or ``--cookiecutter`` for Cookiecutter_ integration.

Find more extensions within the `PyScaffold organisation`_ and consider contributing your own,
it is very easy!
You can quickly generate a template for your extension with the
``--custom-extension`` option after having installed `pyscaffoldext-custom-extension`_.
Have a look in our guide on :ref:`writing extensions <extensions>` to get started.

All extensions can easily be installed with ``pip install pyscaffoldext-NAME``.

Easy Updating
=============

Keep your project's scaffold up-to-date by applying ``putup --update my_project``
when a new version of PyScaffold was released.
An update will only overwrite files that are not often altered by users like
``setup.py``. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!
Please check out the :ref:`updating` docs for more information on how to migrate
from old versions and :ref:`configuration options <configuration>` in ``setup.cfg``.

Adding features
---------------

With the help of an **experimental** updating functionality it is also possible to
add additional features to your existing project scaffold. If a scaffold lacking
``.cirrus.yml`` was created with ``putup my_project`` it can later be added by issuing
``putup my_project --update --cirrus``. For this to work, PyScaffold stores all
options that were initially used to put up the scaffold under the ``[pyscaffold]``
section in ``setup.cfg``. Be aware that right now PyScaffold provides no way to
remove a feature which was once added.

PyScaffold Configuration
========================

After having used PyScaffold for some time, you probably will notice yourself
repeating the same options most of the time for every new project.
Don't worry, PyScaffold now allows you to set default flags using the
**experimental** ``default.cfg`` file [#feat3]_.
Check out our :ref:`Configuration <default-cfg>` section to get started.


.. [#feat1] Tox is a `virtual environment`_ management and test tool that allows
   you to define and run custom tasks that call executables from Python packages.
   In general, PyScaffold will already pre-configure `tox`_ to do the
   most common tasks for you. You can have a look on what is available out of
   the box by running ``tox -av``, or go ahead and check `tox`_ docs to
   automatise your own tasks.

.. [#feat2] The verbose command is intentional here to prevent later regrets.
   Once a package version is published to PyPI, it cannot be replaced.
   Therefore, be always sure your are done and all set before publishing.

.. [#feat3] Experimental features can change the way they work (or be removed)
   between any releases. If you are scripting with PyScaffold, please avoid using them.


.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html
.. _setuptools' documentation: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _namespace packages: https://packaging.python.org/guides/packaging-namespace-packages/
.. _Sphinx: http://www.sphinx-doc.org/
.. _Read the Docs: https://readthedocs.org/
.. _RTD guides: https://docs.readthedocs.io/en/stable/intro/import-guide.html
.. _tox: https://tox.readthedocs.org/
.. _tox documentation: http://tox.readthedocs.org/en/latest/
.. _tox examples: https://tox.readthedocs.io/en/latest/examples.html
.. _tox tutorial: https://www.seanh.cc/2018/09/01/tox-tutorial/
.. _semantic versioning: https://semver.org
.. _Numpy and Google style docstrings: http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _choosealicense.com: https://choosealicense.com/appendix/
.. _Django project: https://www.djangoproject.com/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
.. _pip-tools: https://github.com/jazzband/pip-tools/
.. _Pipenv: https://docs.pipenv.org
.. _PyPI: https://pypi.org/
.. _TestPyPI: https://test.pypi.org/
.. _twine: https://twine.readthedocs.io/
.. _using TestPyPI: https://packaging.python.org/guides/using-testpypi/
.. _importlib.resources: https://docs.python.org/3/library/importlib.html#module-importlib.resources
.. _importlib_resources: https://importlib-resources.readthedocs.io/
.. _flake8: http://flake8.readthedocs.org/
.. _GitLab: https://gitlab.com/
.. _PEP 420: https://www.python.org/dev/peps/pep-0420/
.. _PEP 440: https://www.python.org/dev/peps/pep-0440/
.. _PEP 517: https://www.python.org/dev/peps/pep-0517/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _pre-commit hooks: http://pre-commit.com/
.. _setuptools_scm: https://pypi.python.org/pypi/setuptools_scm/
.. _pytest: http://pytest.org/
.. _Cirrus CI: https://cirrus-ci.org/
.. _pytest-cov: https://github.com/schlamar/pytest-cov
.. _Coveralls: https://coveralls.io/
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _pyscaffoldext-custom-extension: https://github.com/pyscaffold/pyscaffoldext-custom-extension
.. _pyscaffoldext-markdown: https://github.com/pyscaffold/pyscaffoldext-markdown
.. _pyscaffoldext-django: https://github.com/pyscaffold/pyscaffoldext-django
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _PyScaffold organisation: https://github.com/pyscaffold/
.. _dependency hell: https://en.wikipedia.org/wiki/Dependency_hell
.. _pkg_resources: https://setuptools.readthedocs.io/en/latest/pkg_resources.html
.. _make: https://en.wikipedia.org/wiki/Make_(software)
.. _appdirs: https://pypi.org/project/appdirs/
.. _wheels: https://realpython.com/python-wheels/
.. _SPDX index: https://spdx.org/licenses/
.. _Mozilla Public License 2.0: https://choosealicense.com/licenses/mpl-2.0/
.. _editable installs: https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs
.. _virtual environment: https://towardsdatascience.com/virtual-environments-104c62d48c54
.. _TravisCI: https://travis-ci.com
