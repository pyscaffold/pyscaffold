.. image:: https://api.cirrus-ci.com/github/pyscaffold/pyscaffold.svg?branch=master
    :alt: Built Status
    :target: https://cirrus-ci.com/github/pyscaffold/pyscaffold
.. image:: https://readthedocs.org/projects/pyscaffold/badge/?version=latest
    :alt: ReadTheDocs
    :target: https://pyscaffold.org/en/latest
.. image:: https://img.shields.io/coveralls/github/pyscaffold/pyscaffold/master.svg
    :alt: Coveralls
    :target: https://coveralls.io/r/pyscaffold/pyscaffold
.. image:: https://img.shields.io/pypi/v/pyscaffold.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/pyscaffold/
.. image:: https://img.shields.io/conda/vn/conda-forge/pyscaffold.svg
    :alt: Conda-Forge
    :target: https://anaconda.org/conda-forge/pyscaffold
.. image:: https://pepy.tech/badge/pyscaffold/month
    :alt: Monthly Downloads
    :target: https://pepy.tech/project/pyscaffold
.. image:: https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=ff69b4
    :alt: Sponsor me
    :target: https://github.com/sponsors/FlorianWilhelm
.. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
    :alt: Twitter
    :target: https://twitter.com/pyscaffold
.. image:: https://img.shields.io/badge/-PyScaffold?style=social&logo=pyscaffold&logoColor=005CA0&label=PyScaffold
    :alt: PyScaffold
    :target: https://pyscaffold.org/

|

.. image:: https://pyscaffold.org/en/latest/_images/logo.png
    :height: 512px
    :width: 512px
    :scale: 60 %
    :alt: PyScaffold logo
    :align: center

|

PyScaffold is a project generator for bootstrapping high quality Python
packages, ready to be shared on PyPI_ and installable via pip_.
It is easy to use and encourages the adoption of the best tools and
practices of the Python ecosystem, helping you and your team
to stay sane, happy and productive. The best part? It is stable and has been used
by thousands of developers for over half a decade!

Checkout out `this demo project`_, which was set up using PyScaffold and
if you are still not convinced yet, also have a look at these `reasons to use PyScaffold`_.


    **NOTE** - This document refers to the latest version of PyScaffold (v4).
    Please refer to `v3.3`_ for the previous stable version.


Quickstart
==========

Just pick your favourite installation method::

    ## Good old pip
    # (make sure it is up-to-date: pip install -U pip setuptools)
    pip install pyscaffold

    ## Conda for the datascience fans
    conda install -c conda-forge pyscaffold

    ## Or even pipx for the virtualenv aficionados
    pipx install pyscaffold

If you want to install all PyScaffold's *extensions* you can even::

    pip install pyscaffold[all]

(More details of each method are available in the `installation docs`_)

After the installation, a new ``putup`` command will be available and you can just type::

    putup my_project

This will create a new folder called ``my_project`` containing a perfect *project
template* with everything you need for some serious coding.

After ``cd``-ing into your new project and creating (or activating) an `isolated
development environment`_ (with virtualenv_, conda_ or your preferred tool),
you can do the usual `editable install`_::

    pip install -e .

… all set and ready to go!

We also recommend using tox_, so you can take advantage of the automation tasks
we have setup for you, like::

   tox -e build  # to build your package distribution
   tox -e publish  # to test your project uploads correctly in test.pypi.org
   tox -e publish -- --repository pypi  # to release your package to PyPI
   tox -av  # to list all the tasks available

The following figure demonstrates the usage of ``putup`` with the new experimental
interactive mode for setting up a simple project.
It uses the `--cirrus` flag to add CI support (via `Cirrus CI`_), and
tox_ to run automated project tasks like building a package file for
distribution (or publishing).

.. image:: https://pyscaffold.org/en/latest/_images/demo.gif
    :alt: Creating a simple package with PyScaffold
    :target: https://asciinema.org/a/qzh5ZYKl1q5xYEnM4CHT04HdW?autoplay=1

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have Git_ installed and set up on your PC,
meaning at least your name and email are configured.

The project template provides you with following features:


Configuration & Packaging
=========================

All configuration can be done in ``setup.cfg`` like changing the description,
URL, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.

In order to build a source or wheel distribution, just run ``tox -e build``
(if you don't use tox_, you can also install ``build`` and run ``python -m build``).

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that reside within your package and
are tracked by Git will automatically be included
if ``include_package_data = True`` in ``setup.cfg``.
It is not necessary to have a ``MANIFEST.in`` file for this to work.

Note that the ``include_package_data`` option in ``setup.cfg`` is only
guaranteed to be read when creating a `wheels`_ distribution. Other distribution methods might
behave unexpectedly (e.g. always including data files even when
``include_package_data = False``). Therefore, the best option if you want to have
data files in your repository **but not as part of the pip installable package**
is to add them somewhere **outside** the ``src`` directory (e.g. a ``files``
directory in the root of the project, or inside ``tests`` if you use them for
checks). Additionally you can exclude them explicitly via the
``[options.packages.find] exclude`` option in ``setup.cfg``.


Versioning and Git Integration
==============================

Your project is an already initialised Git repository and uses
the information of tags to infer the version of your project with the help of
setuptools_scm_.
To use this feature, you need to tag with the format ``MAJOR.MINOR[.PATCH]``
, e.g. ``0.0.1`` or ``0.1``.
This version will be used when building a package and is also accessible
through ``my_project.__version__``.

Unleash the power of Git by using its `pre-commit hooks`_. This feature is
available through the ``--pre-commit`` flag. After your project's scaffold
was generated, make sure pre-commit is installed, e.g. ``pip install pre-commit``,
then just run ``pre-commit install``.

A default ``.gitignore`` file is also provided; it is
well adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

PyScaffold will prepare a `docs` directory with all you need to start writing
your documentation.
Start editing the file ``docs/index.rst`` to extend the documentation.
The documentation also works with `Read the Docs`_.

The `Numpy and Google style docstrings`_ are activated by default.

If you have `tox`_ in your system, simply run ``tox -e docs`` or ``tox -e
doctests`` to compile the docs or run the doctests.

Alternatively, if you have `make`_ and `Sphinx`_ installed in your computer, build the
documentation with ``make -C docs html`` and run doctests with
``make -C docs doctest``. Just make sure Sphinx 1.3 or above is installed.


Automation, Tests & Coverage
============================

PyScaffold relies on `pytest`_ to run all automated tests defined in the subfolder
``tests``.  Some sane default flags for pytest are already defined in the
``[tool:pytest]`` section of ``setup.cfg``. The pytest plugin `pytest-cov`_ is used
to automatically generate a coverage report. It is also possible to provide
additional parameters and flags on the commandline, e.g., type::

    pytest -h

to show the help of pytest (requires `pytest`_ to be installed in your system
or virtualenv).

Projects generated with PyScaffold by default support running tests via `tox`_,
a virtualenv management and test tool, which is very handy. If you run::

    tox

in the root of your project, `tox`_ will download its dependencies, build the
package, install it in a virtualenv and run the tests using `pytest`_, so you
are sure everything is properly tested.


.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--cirrus`` to generate
templates of the `Cirrus CI`_ configuration file ``.cirrus.yml`` which even
features the coverage and stats system `Coveralls`_.


Management of Requirements & Licenses
=====================================

Installation requirements of your project can be defined inside ``setup.cfg``,
e.g. ``install_requires = numpy; scipy``. To avoid package dependency problems
it is common to not pin installation requirements to any specific version,
although minimum versions, e.g. ``sphinx>=1.3``, and/or maximum versions, e.g.
``pandas<0.12``, are used frequently in accordance with `semantic versioning`_.

All licenses from `choosealicense.com`_ can be easily selected with the help
of the ``--license`` flag.


Extensions
==========

PyScaffold comes with several extensions:

* If you want a project setup for a *Data Science* task, just use ``--dsproject``
  after having installed `pyscaffoldext-dsproject`_.

* Have a ``README.md`` based on Markdown instead of ``README.rst`` by using
  ``--markdown`` after having installed `pyscaffoldext-markdown`_.

* Create a `Django project`_ with the flag ``--django`` which is equivalent to
  ``django-admin startproject my_project`` enhanced by PyScaffold's features
  (requires `pyscaffoldext-django`_).

* … and many more like ``--gitlab`` to create the necessary files for GitLab_,
  ``--travis`` for `Travis CI`_ (see `pyscaffoldext-travis`_), or
  ``--cookiecutter`` for Cookiecutter_ integration (see `pyscaffoldext-cookiecutter`_).

Find more extensions within the `PyScaffold organisation`_ and consider contributing your own,
it is very easy! You can quickly generate a template for your extension with the
``--custom-extension`` option after having installed `pyscaffoldext-custom-extension`_.

All extensions can easily be installed with ``pip install pyscaffoldext-NAME``.

Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putup --update my_project`` when a new version of PyScaffold was released.
An update will only overwrite files that are not often altered by users like
``setup.py``. To update all files use ``--update --force``.
An existing project that was not setup with PyScaffold can be converted with
``putup --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!


.. _v3.3: https://pyscaffold.org/en/v3.3.x/
.. _PyPI: https://pypi.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _this demo project: https://github.com/pyscaffold/pyscaffold-demo
.. _reasons to use PyScaffold: https://pyscaffold.org/en/latest/reasons.html
.. _installation docs: https://pyscaffold.org/en/latest/install.html
.. _isolated development environment: https://realpython.com/python-virtual-environments-a-primer/
.. also good, but sometimes medium can get on the way: https://towardsdatascience.com/virtual-environments-104c62d48c54
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _conda: https://docs.conda.io/en/latest/
.. _editable install: https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs
.. _setuptools: https://setuptools.pypa.io/en/stable/userguide/declarative_config.html
.. _setuptools_scm: https://pypi.org/project/setuptools-scm/
.. _semantic versioning: https://semver.org
.. _Git: https://git-scm.com/
.. _PEP440: https://www.python.org/dev/peps/pep-0440/
.. _pre-commit hooks: https://pre-commit.com/
.. _make: https://www.gnu.org/software/make/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Read the Docs: https://readthedocs.org/
.. _Numpy and Google style docstrings: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _pytest: https://docs.pytest.org/en/stable/
.. _pytest-cov: https://github.com/pytest-dev/pytest-cov
.. _Cirrus CI: https://cirrus-ci.org/
.. _Travis CI: https://travis-ci.org/
.. _Coveralls: https://coveralls.io/
.. _tox: https://tox.wiki/en/stable/
.. _choosealicense.com: https://choosealicense.com/
.. _Django project: https://www.djangoproject.com/
.. _Cookiecutter: https://cookiecutter.readthedocs.io/en/stable/
.. _GitLab: https://about.gitlab.com/
.. _pip-tools: https://github.com/jazzband/pip-tools/
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _pyscaffoldext-custom-extension: https://github.com/pyscaffold/pyscaffoldext-custom-extension
.. _pyscaffoldext-markdown: https://github.com/pyscaffold/pyscaffoldext-markdown
.. _pyscaffoldext-django: https://github.com/pyscaffold/pyscaffoldext-django
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _pyscaffoldext-travis: https://github.com/pyscaffold/pyscaffoldext-travis
.. _PyScaffold organisation: https://github.com/pyscaffold/
.. _wheels: https://realpython.com/python-wheels/
