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
url, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.
The syntax of ``setup.cfg`` is pretty much self-explanatory and well commented,
check out this :ref:`example <configuration>` or `setuptools' documentation`_.

In order to build a source, binary or wheel distribution, just run
``python setup.py sdist``, ``python setup.py bdist`` or
``python setup.py bdist_wheel`` (recommended).

.. rubric:: Uploading to PyPI

Of course uploading your package to the official Python package index PyPI_
for distribution also works out of the box. Just create a distribution as
mentioned above and use twine_ to upload it to PyPI_, e.g.::

    pip install twine
    twine upload dist/*

For this to work, you have to first register a PyPI_ account. If you just
want to test, please be kind and `use TestPyPI`_ before uploading to PyPI_.

Please also note that PyPI_ does not allow uploading local versions
for practical reasons. Thus, you have to create a git tag before uploading a version
of your distribution. Read more about it in the versioning_ section below.

.. warning::
    Be aware that the usage of ``python setup.py upload`` for PyPI_ uploads
    also works but is nowadays strongly discouraged and even some
    of the new PyPI_ features won't work correctly if you don't use twine_.

.. rubric:: Namespace Packages

Optionally, `namespace packages`_ can be used, if you are planning to distribute
a larger package as a collection of smaller ones. For example, use::

    putup my_project --package my_package --namespace com.my_domain

to define ``my_package`` inside the namespace ``com.my_domain`` in java-style.

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that **must reside within** your package, e.g.
under ``my_project/src/my_package``, and are tracked by Git will automatically be included
(``include_package_data = True`` in ``setup.cfg``).
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
Even another way, provided by `setuptools`_'s  `pkg_resources`_ is::

    from pkg_resources import resource_string
    data = resource_string(__name__, 'path/to/my/data/relative/to/module.txt')

Yes, actually "there should be one-- and preferably only one --obvious way to do it." ;-)

Please have in mind that the ``include_package_data`` option in ``setup.cfg`` is only
guaranteed to be read when creating `wheels`_. Other distribution methods might
behave unexpectedly (e.g. always including data files even when
``include_package_data=False``). Therefore, the best option if you want to have
data files in your repository **but not as part of the pip installable package**
is to add them somewhere **outside** the ``src`` directory (e.g. a ``files``
directory in the root of the project, or inside ``tests`` if you use them for
checks). Additionally you can exclude them explicitly via the
``[options.packages.find] exclude`` option in ``setup.cfg``.

.. warning::
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

Your project is already an initialised Git repository and ``setup.py`` uses
the information of tags to infer the version of your project with the help of `setuptools_scm`_.
To use this feature you need to tag with the format ``MAJOR.MINOR[.PATCH]``
, e.g. ``0.0.1`` or ``0.1``.
Run ``python setup.py --version`` to retrieve the current `PEP440`_-compliant version.
This version will be used when building a package and is also accessible through
``my_project.__version__``. If you want to upload to PyPI_ you have to tag the current commit
before uploading since PyPI_ does not allow local versions, e.g. ``0.0.post0.dev5+gc5da6ad``,
for practical reasons.

.. rubric:: Best Practices and Common Errors with Version Numbers

* **How do I get a clean version like 3.2.4 when I have 3.2.3.post0.dev9+g6817bd7?**
  Just commit all your changes and create a new tag using ``git tag v3.2.4``. In order to build an old version
  checkout an old tag, e.g. ``git checkout -b v3.2.3 v3.2.3`` and run ``python setup.py bdist_wheel``.

* **Why do I see `unknown` as version?**
  In most cases this happens if your source code is no longer a proper Git repository, maybe because
  you moved or copied it or Git is not even installed. In general using ``python setup.py install``
  (or ``develop``) to install your package is only recommended for developers of your Python project,
  which have Git installed and use a proper Git repository anyway. Users of your project should always
  install it using the distribution you built for them e.g. ``pip install my_project-3.2.3-py3-none-any.whl``.
  You build such a distribution by running ``python setup.py bdist_wheel`` and then find it under ``./dist``.

* **Is there a good versioning scheme I should follow?**
  The most common practice is to use `Semantic Versioning`_. Following this practice avoids the so called
  `dependency hell`_ for the users of your package. Also be sure to set attributes like ``python_requires``
  and ``install_requires`` appropriately in ``setup.cfg``.

* **Is there a best practise for distributing my package?**
  First of all, cloning your repository or just coping your code around is a really bad practice which comes
  with tons of pitfalls. The *clean* way is to first build a distribution and then give this distribution to
  your users. This can be done by just copying the distribution file or uploading it to some artifact store
  like `PyPI`_ for public packages or `devpi`_, `Nexus`_, etc. for private packages. Also check out this
  article about `packaging, versioning and continuous integration`_.

* **Using some CI service, why is the version `unknown` or `my_project-0.0.post0.dev50`?**
  Some CI services use shallow git clones, i.e. ``--depth N``, or don't download git tags to save bandwidth.
  To verify that your repo works as expected, run::

    git describe --dirty --tags --long --first-parent

  which is basically what `setuptools_scm`_ does to retrieve the correct version number. If this command
  fails, tweak how your repo is cloned depending on your CI service and make sure to also download the tags,
  i.e. ``git fetch origin --tags``.


.. rubric:: Pre-commit Hooks

Unleash the power of Git by using its `pre-commit hooks`_.
This feature is available through the  ``--pre-commit`` flag.
After your project's scaffold was generated, make sure pre-commit is
installed, e.g. ``pip install pre-commit``, then just run ``pre-commit install``.

It goes unsaid that also a default ``.gitignore`` file is provided that is well
adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

PyScaffold will prepare a `docs` directory with all you need to start writing
your documentation.
Start editing the file ``docs/index.rst`` to extend the documentation.
The documentation also works with `Read the Docs`_.

The `Numpy and Google style docstrings`_ are activated by default.
Just make sure Sphinx 1.3 or above is installed.

If you have `make`_ and `Sphinx`_ installed in your computer, build the
documentation with ``make -C docs html`` and run doctests with
``make -C docs doctest``.
Alternatively, if your project was created with the ``--tox``
option, simply run ``tox -e docs`` ot ``tox -e doctests``.


Dependency Management in a Breeze
=================================

PyScaffold out of the box allows developers to express abstract dependencies
and take advantage of ``pip`` to manage installation. It also can be used
together with a virtual environment to avoid *dependency hell* during both
development and production stages.

In particular, PyPA's `Pipenv`_ can be integrated in any PyScaffold-generated
project by following standard `setuptools`_ conventions.  Keeping abstract
requirements in ``setup.cfg`` and running ``pipenv install -e .`` is basically
what you have to do (details in :ref:`Dependency Management <dependencies>`).

.. warning::

    *Experimental Feature* - Pipenv support is experimental and might change in
    the future


Unittest & Coverage
===================

PyScaffold relies on `py.test`_ to run all unittests defined in the subfolder
``tests``.  Some sane default flags for py.test are already defined in the
``[pytest]`` section of ``setup.cfg``. The py.test plugin `pytest-cov`_ is used
to automatically generate a coverage report. It is also possible to provide
additional parameters and flags on the commandline, e.g., type::

    py.test -h

to show the help of py.test (requires `py.test`_ to be installed in your system
or virtualenv).

.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--travis`` to generate
templates of the `Travis`_ configuration files
``.travis.yml`` and ``tests/travis_install.sh`` which even features the
coverage and stats system `Coveralls`_.
In order to use the virtualenv management and test tool `tox`_
the flag ``--tox`` can be specified.
If you are using `GitLab`_ you can get a default
`.gitlab-ci.yml` also running `pytest-cov` with the flag ``--gitlab``.

.. rubric:: Managing test environments with tox

Run ``tox`` to generate test virtual environments for various python
environments defined in the generated :file:`tox.ini`. Testing and building
*sdists* for python 2.7 and python 3.4 is just as simple with tox as::

        tox -e py27,py34

Environments for tests with the the static code analyzers pyflakes and pep8
which are bundled in `flake8`_ are included
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


* If you want a project setup for a *Data Science* task, just use ``--dsproject``
  after having installed `pyscaffoldext-dsproject`_.

* Create a `Django project`_ with the flag ``--django`` which is equivalent to
  ``django-admin startproject my_project`` enhanced by PyScaffold's features.

* Create a template for your own PyScaffold extension with ``--custom-extension``
  after having installed `pyscaffoldext-custom-extension`_ with ``pip``.

* Have a ``README.md`` based on MarkDown instead of ``README.rst`` by using
  ``--markdown`` after having installed `pyscaffoldext-markdown`_ with ``pip``.

* Add a ``pyproject.toml`` file according to `PEP 518`_ to your template by using
  ``--pyproject`` after having installed `pyscaffoldext-pyproject`_ with ``pip``.

* With the help of `Cookiecutter`_ it is possible to further customize your project
  setup with a template tailored for PyScaffold. Just use the flag ``--cookiecutter TEMPLATE``
  to use a cookiecutter template which will be refined by PyScaffold afterwards.

* ... and many more like ``--gitlab`` to create the necessary files for GitLab_.

There is also documentation about :ref:`writing extensions <extensions>`. Find more
extensions within the `PyScaffold organisation`_ and consider contributing your own.
All extensions can easily be installed with ``pip install pyscaffoldext-NAME``.

.. warning::

    *Deprecation Notice* - In the next major release both Cookiecutter and
    Django extensions will be extracted into independent packages.  After
    PyScaffold v4.0, you will need to explicitly install
    ``pyscaffoldext-cookiecutter`` and ``pyscaffoldext-django`` in your
    system/virtualenv in order to be able to use them.

Easy Updating
=============

Keep your project's scaffold up-to-date by applying
``putup --update my_project`` when a new version of PyScaffold was released.
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
options that were initially used to put up the scaffold under the ``[pyscaffold]``
section in ``setup.cfg``. Be aware that right now PyScaffold provides no way to
remove a feature which was once added.


.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html
.. _setuptools' documentation: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _namespace packages: https://packaging.python.org/guides/packaging-namespace-packages/
.. _Sphinx: http://www.sphinx-doc.org/
.. _Read the Docs: https://readthedocs.org/
.. _tox documentation: http://tox.readthedocs.org/en/latest/
.. _Numpy and Google style docstrings: http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _choosealicense.com: http://choosealicense.com/
.. _Django project: https://www.djangoproject.com/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
.. _pip-tools: https://github.com/jazzband/pip-tools/
.. _Pipenv: https://docs.pipenv.org
.. _PyPI: https://pypi.org/
.. _twine: https://twine.readthedocs.io/
.. _use TestPyPI: https://packaging.python.org/guides/using-testpypi/
.. _importlib.resources: https://docs.python.org/3/library/importlib.html#module-importlib.resources
.. _importlib_resources: https://importlib-resources.readthedocs.io/
.. _pkg_resources: https://setuptools.readthedocs.io/en/latest/pkg_resources.html
.. _flake8: http://flake8.readthedocs.org/
.. _GitLab: https://gitlab.com/
.. _tox: https://tox.readthedocs.org/
.. _PEP440: http://www.python.org/dev/peps/pep-0440/
.. _pre-commit hooks: http://pre-commit.com/
.. _setuptools_scm: https://pypi.python.org/pypi/setuptools_scm/
.. _py.test: http://pytest.org/
.. _Travis: https://travis-ci.org/
.. _pytest-cov: https://github.com/schlamar/pytest-cov
.. _Coveralls: https://coveralls.io/
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _pyscaffoldext-custom-extension: https://github.com/pyscaffold/pyscaffoldext-custom-extension
.. _pyscaffoldext-markdown: https://github.com/pyscaffold/pyscaffoldext-markdown
.. _pyscaffoldext-pyproject: https://github.com/pyscaffold/pyscaffoldext-pyproject
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _PyScaffold organisation: https://github.com/pyscaffold/
.. _Semantic Versioning: https://semver.org/
.. _dependency hell: https://en.wikipedia.org/wiki/Dependency_hell
.. _devpi: https://devpi.net/
.. _Nexus: https://www.sonatype.com/product-nexus-repository
.. _packaging, versioning and continuous integration: https://florianwilhelm.info/2018/01/ds_in_prod_packaging_ci/
.. _make: https://en.wikipedia.org/wiki/Make_(software)
.. _appdirs: https://pypi.org/project/appdirs/
.. _wheels: https://realpython.com/python-wheels/
