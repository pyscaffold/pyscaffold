=================================
pbr - Python Build Reasonableness
=================================

A library for managing setuptools packaging needs in a consistent manner.

`pbr` reads and then filters the `setup.cfg` data through a setup hook to
fill in default values and provide more sensible behaviors, and then feeds
the results in as the arguments to a call to `setup.py` - so the heavy
lifting of handling python packaging needs is still being done by
`setuptools`.

Note that we don't support the `easy_install` aspects of setuptools: while
we depend on setup_requires, for any install_requires we recommend that they
be installed prior to running `setup.py install` - either by hand, or by using
an install tool such as `pip`.

What It Does
============

PBR can and does do a bunch of things for you:

* **Version**: Manage version number based on git revisions and tags
* **AUTHORS**: Generate AUTHORS file from git log
* **ChangeLog**: Generate ChangeLog from git log
* **Manifest**: Generate a sensible manifest from git files and some standard
  files
* **Sphinx Autodoc**: Generate autodoc stub files for your whole module
* **Requirements**: Store your dependencies in a pip requirements file
* **long_description**: Use your README file as a long_description
* **Smart find_packages**: Smartly find packages under your root package

Version
-------

Versions can be managed two ways - postversioning and preversioning.
Postversioning is the default, and preversioning is enabled by setting
``version`` in the setup.cfg ``metadata`` section. In both cases version
strings are inferred from git.

If the currently checked out revision is tagged, that tag is used as
the version.

If the currently checked out revision is not tagged, then we take the
last tagged version number and increment it to get a minimum target
version.

We then walk git history back to the last release. Within each commit we look
for a Sem-Ver: pseudo header, and if found parse it looking for keywords.
Unknown symbols are not an error (so that folk can't wedge pbr or break their
tree), but we will emit an info level warning message. Known symbols:
``feature``, ``api-break``, ``deprecation``, ``bugfix``. A missing
Sem-Ver line is equivalent to ``Sem-Ver: bugfix``. The ``bugfix`` symbol causes
a patch level increment to the version. The ``feature`` and ``deprecation``
symbols cause a minor version increment. The ``api-break`` symbol causes a
major version increment.

If postversioning is in use, we use the resulting version number as the target
version.

If preversioning is in use we check that the version set in the metadata
section of `setup.cfg` is greater than the version we infer using the above
method.  If the inferred version is greater than the preversioning value we
raise an error, otherwise we use the version from `setup.cfg` as the target.

We then generate dev version strings based on the commits since the last
release and include the current git sha to disambiguate multiple dev versions
with the same number of commits since the release.

.. note::

   `pbr` expects git tags to be signed for use in calculating versions

The versions are expected to be compliant with :doc:`semver`.

The ``version.SemanticVersion`` class can be used to query versions of a
package and present it in various forms - ``debian_version()``,
``release_string()``, ``rpm_string()``, ``version_string()``, or
``version_tuple()``.

AUTHORS and ChangeLog
---------------------

Why keep an `AUTHORS` or a `ChangeLog` file when git already has all of the
information you need? `AUTHORS` generation supports filtering/combining based
on a standard `.mailmap` file.

Manifest
--------

Just like `AUTHORS` and `ChangeLog`, why keep a list of files you wish to
include when you can find many of these in git. `MANIFEST.in` generation
ensures almost all files stored in git, with the exception of `.gitignore`,
`.gitreview` and `.pyc` files, are automatically included in your
distribution. In addition, the generated `AUTHORS` and `ChangeLog` files are
also included. In many cases, this removes the need for an explicit
'MANIFEST.in' file

Sphinx Autodoc
--------------

Sphinx can produce auto documentation indexes based on signatures and
docstrings of your project but you have to give it index files to tell it
to autodoc each module: that's kind of repetitive and boring. PBR will scan
your project, find all of your modules, and generate all of the stub files for
you.

Sphinx documentation setups are altered to generate man pages by default. They
also have several pieces of information that are known to setup.py injected
into the sphinx config.

See the pbr_ section for details on configuring your project for autodoc.

Requirements
------------

You may not have noticed, but there are differences in how pip
`requirements.txt` files work and how distutils wants to be told about
requirements. The pip way is nicer because it sure does make it easier to
populate a virtualenv for testing or to just install everything you need.
Duplicating the information, though, is super lame. To solve this issue, `pbr`
will let you use `requirements.txt`-format files to describe the requirements
for your project and will then parse these files, split them up appropriately,
and inject them into the `install_requires`, `tests_require` and/or
`dependency_links` arguments to `setup`. Voila!

You can also have a requirement file for each specific major version of Python.
If you want to have a different package list for Python 3 then just drop a
`requirements-py3.txt` and it will be used instead.

Finally, it is possible to specify groups of optional dependencies, or
`"extra" requirements`_, in your `setup.cfg` rather than `setup.py`.

long_description
----------------

There is no need to maintain two long descriptions- and your README file is
probably a good long_description. So we'll just inject the contents of your
README.rst, README.txt or README file into your empty long_description. Yay
for you.

Usage
=====

`pbr` is a setuptools plugin and so to use it you must use setuptools and call
``setuptools.setup()``. While the normal setuptools facilities are available,
pbr makes it possible to express them through static data files.

.. _setup_py:

setup.py
--------

`pbr` only requires a minimal `setup.py` file compared to a standard setuptools
project. This is because most configuration is located in static configuration
files. This recommended minimal `setup.py` file should look something like this::

    #!/usr/bin/env python

    from setuptools import setup

    setup(
        setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
        pbr=True,
    )

.. note::

   It is necessary to specify ``pbr=True`` to enabled `pbr` functionality.

.. note::

   While one can pass any arguments supported by setuptools to `setup()`,
   any conflicting arguments supplied in `setup.cfg` will take precedence.

setup.cfg
---------

The `setup.cfg` file is an ini-like file that can mostly replace the `setup.py`
file. It is based on the distutils2_ `setup.cfg` file. A simple sample can be
found in `pbr`'s own `setup.cfg` (it uses its own machinery to install
itself)::

    [metadata]
    name = pbr
    author = OpenStack Foundation
    author-email = openstack-dev@lists.openstack.org
    summary = OpenStack's setup automation in a reusable form
    description-file = README
    home-page = https://launchpad.net/pbr
    license = Apache-2
    classifier =
        Development Status :: 4 - Beta
        Environment :: Console
        Environment :: OpenStack
        Intended Audience :: Developers
        Intended Audience :: Information Technology
        License :: OSI Approved :: Apache Software License
        Operating System :: OS Independent
        Programming Language :: Python
    keywords =
        setup
        distutils

    [files]
    packages =
        pbr
    data_files =
        etc/pbr = etc/*
        etc/init =
            pbr.packaging.conf
            pbr.version.conf

    [entry_points]
    console_scripts =
        pbr = pbr.cmd:main
    pbr.config.drivers =
        plain = pbr.cfg.driver:Plain

`pbr` provides its own section in these documents, ostensibly called ``pbr``,
and provides a custom version of Sphinx's ``build_sphinx`` section. Most other
sections are provided by setuptools and may influence either the build itself
or the output of various `setuptools commands`__. The remaining sections are
provided by libraries that provide setuptools extensions, such as
``extract_mesages`` (provided by `Babel`__). Some of these are described below.

__ https://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
__ http://babel.pocoo.org/en/latest/setup.html
__ http://www.sphinx-doc.org/en/stable/setuptools.html

.. note::

   Comments may be used in `setup.cfg`, however all comments should start with
   a `#` and may be on a single line, or in line, with at least one white space
   character immediately preceding the `#`. Semicolons are not a supported
   comment delimiter. For instance::

       [section]
       # A comment at the start of a dedicated line
       key =
           value1 # An in line comment
           value2
           # A comment on a dedicated line
           value3

files
~~~~~

The ``files`` section defines the install location of files in the package
using three fundamental keys: ``packages``, ``namespace_packages``, and
``data_files``.

``packages``

  A list of top-level packages that should be installed. The behavior of
  packages is similar to ``setuptools.find_packages`` in that it recurses the
  python package hierarchy below the given top level and installs all of it. If
  ``packages`` is not specified, it defaults to the value of the ``name`` field
  given in the ``[metadata]`` section.

``namespace_packages``

  Similar to ``packages``, but is a list of packages that provide namespace
  packages.

``data_files``

  A list of files to be installed. The format is an indented block that
  contains key value pairs which specify target directory and source file to
  install there. More than one source file for a directory may be indicated
  with a further indented list. Source files are stripped of leading
  directories.  Additionally, `pbr` supports a simple file globbing syntax for
  installing entire directory structures, thus::

   [files]
   data_files =
       etc/pbr = etc/pbr/*
       etc/neutron =
           etc/api-paste.ini
           etc/dhcp-agent.ini
       etc/init.d = neutron.init

  will result in `/etc/neutron` containing `api-paste.ini` and `dhcp-agent.ini`,
  both of which pbr will expect to find in the `etc` directory in the root of
  the source tree. Additionally, `neutron.init` from that dir will be installed
  in `/etc/init.d`. All of the files and directories located under `etc/pbr` in
  the source tree will be installed into `/etc/pbr`.

  Note that this behavior is relative to the effective root of the environment
  into which the packages are installed, so depending on available permissions
  this could be the actual system-wide `/etc` directory or just a top-level
  `etc` subdirectory of a virtualenv.

pbr
~~~

The ``pbr`` section controls `pbr` specific options and behaviours.

``autodoc_tree_index_modules``

  A boolean option controlling whether `pbr` should generate an index of
  modules using `sphinx-apidoc`. By default, all files except `setup.py` are
  included, but this can be overridden using the ``autodoc_tree_excludes``
  option.

``autodoc_tree_excludes``

  A list of modules to exclude when building documentation using
  `sphinx-apidoc`. Defaults to ``[setup.py]``. Refer to the `sphinx-apidoc man
  page`_ for more information.

``autodoc_index_modules``

  A boolean option controlling whether `pbr` should itself generates
  documentation for Python modules of the project. By default, all found Python
  modules are included; some of them can be excluded by listing them in
  ``autodoc_exclude_modules``.

``autodoc_exclude_modules``

  A list of modules to exclude when building module documentation using `pbr`.
  `fnmatch` style pattern (e.g. `myapp.tests.*`) can be used.

``api_doc_dir``

  A subdirectory inside the ``build_sphinx.source_dir`` where
  auto-generated API documentation should be written, if
  ``autodoc_index_modules`` is set to True. Defaults to ``"api"``.

.. note::

   When using ``autodoc_tree_excludes`` or ``autodoc_index_modules`` you may
   also need to set ``exclude_patterns`` in your Sphinx configuration file
   (generally found at `doc/source/conf.py` in most OpenStack projects)
   otherwise Sphinx may complain about documents that are not in a toctree.
   This is especially true if the ``[sphinx_build] warning-is-error`` option is
   set. See the `Sphinx build configuration file`_ documentation for more
   information on configuring Sphinx.

.. versionchanged:: 2.0

   The ``pbr`` section used to take a ``warnerrors`` option that would enable
   the ``-W`` (Turn warnings into errors.) option when building Sphinx. This
   feature was broken in 1.10 and was removed in pbr 2.0 in favour of the
   ``[build_sphinx] warning-is-error`` provided in Sphinx 1.5+.

build_sphinx
~~~~~~~~~~~~

The ``build_sphinx`` section is a version of the ``build_sphinx`` setuptools
plugin provided with Sphinx. This plugin extends the original plugin to add the
following:

- Automatic generation of module documentation using the apidoc__ tool

- Automatic configuration of the `project`, `version` and `release` settings
  using information from `pbr` itself

- Support for multiple builders using the ``builders`` configuration option

  .. note::

     Sphinx 1.6 adds support for multiple builders using the default `builder`
     option. You should refer to this file for more information.

The version of ``build_sphinx`` provided by `pbr` provides a single additional
option.

``builders``

  A space or comma separated list of builders to run. For example, to build
  both HTML and man page documentation, you would define the following in your
  `setup.cfg`:

  .. code-block:: ini

      [build_sphinx]
      builders = html,man
      source-dir = doc/source
      build-dir = doc/build
      all-files = 1

``source_dir``

  The path to the source directory where the Sphinx documentation tree
  is.

For information on the remaining options, refer to the `Sphinx
documentation`__. In addition, the ``autodoc_index_modules``,
``autodoc_tree_index_modules``, ``autodoc_exclude_modules`` and
``autodoc_tree_excludes`` options in the ``pbr`` section will affect the output
of the automatic module documentation generation.

.. versionchanged:: 3.0

   The ``build_sphinx`` plugin used to default to building both HTML and man
   page output. This is no longer the case, and you should explicitly set
   ``builders`` to ``html man`` if you wish to retain this behavior.

__ http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
__ http://www.sphinx-doc.org/en/stable/setuptools.html

entry_points
~~~~~~~~~~~~

The ``entry_points`` section defines entry points for generated console scripts
and python libraries. This is actually provided by `setuptools`__ but is
documented here owing to its importance.

The general syntax of specifying entry points is a top level name indicating
the entry point group name, followed by one or more key value pairs naming
the entry point to be installed. For instance::

    [entry_points]
    console_scripts =
        pbr = pbr.cmd:main
    pbr.config.drivers =
        plain = pbr.cfg.driver:Plain
        fancy = pbr.cfg.driver:Fancy

Will cause a console script called `pbr` to be installed that executes the
`main` function found in `pbr.cmd`. Additionally, two entry points will be
installed for `pbr.config.drivers`, one called `plain` which maps to the
`Plain` class in `pbr.cfg.driver` and one called `fancy` which maps to the
`Fancy` class in `pbr.cfg.driver`.

__ https://setuptools.readthedocs.io/en/latest/setuptools.html#options

Requirements
------------

Requirement files should be given one of the below names. This order is also
the order that the requirements are tried in (where `N` is the Python major
version number used to install the package):

* requirements-pyN.txt
* tools/pip-requires-py3
* requirements.txt
* tools/pip-requires

Only the first file found is used to install the list of packages it contains.

.. note::

   The 'requirements-pyN.txt' file is deprecated - 'requirements.txt' should
   be universal. You can use `Environment markers`_ for this purpose.

Extra requirements
~~~~~~~~~~~~~~~~~~

Groups of optional dependencies, or `"extra" requirements`_, can be described
in your `setup.cfg`, rather than needing to be added to `setup.py`. An example
(which also demonstrates the use of environment markers) is shown below.

Environment markers
~~~~~~~~~~~~~~~~~~~

Environment markers are `conditional dependencies`_ which can be added to the
requirements (or to a group of extra requirements) automatically, depending
on the environment the installer is running in. They can be added to
requirements in the requirements file, or to extras defined in `setup.cfg`,
but the format is slightly different for each.

For ``requirements.txt``::

    argparse; python_version=='2.6'

This will result in the package depending on ``argparse`` only if it's being
installed into Python 2.6

For extras specified in `setup.cfg`, add an ``extras`` section. For instance,
to create two groups of extra requirements with additional constraints on the
environment, you can use::

    [extras]
    security =
        aleph
        bet:python_version=='3.2'
        gimel:python_version=='2.7'
    testing =
        quux:python_version=='2.7'


Testing
-------

`pbr` overrides the ``setuptools`` hook ``test`` (i.e. ``setup.py test``). The
following sequence is followed:

#. If a ``.testr.conf`` file exists and `testrepository
   <https://pypi.python.org/pypi/testrepository>`__ is installed, `pbr`
   will use it as the test runner.  See the ``testr`` documentation
   for more details.

   .. note::

     This is separate to ``setup.py testr`` (note the extra ``r``) which
     is provided directly by the ``testrepository`` package.  Be careful
     as there is some overlap of command arguments.

#. Although deprecated, if ``[nosetests]`` is defined in ``setup.cfg``
   and `nose <http://nose.readthedocs.io/en/latest/>`__ is installed,
   the ``nose`` runner will be used.

#. In other cases no override will be installed and the ``test``
   command will revert to `setuptools
   <http://setuptools.readthedocs.io/en/latest/setuptools.html#test-build-package-and-run-a-unittest-suite>`__.

A typical usage would be in ``tox.ini`` such as::

  [tox]
  minversion = 2.0
  skipsdist = True
  envlist = py33,py34,py35,py26,py27,pypy,pep8,docs

  [testenv]
  usedevelop = True
  setenv =
    VIRTUAL_ENV={envdir}
    CLIENT_NAME=pbr
  deps = .
       -r{toxinidir}/test-requirements.txt
  commands =
    python setup.py test --testr-args='{posargs}'

The argument ``--coverage`` will set ``PYTHON`` to ``coverage run`` to
produce a coverage report.  ``--coverage-package-name`` can be used to
modify or narrow the packages traced.

Additional Docs
===============

.. toctree::
   :maxdepth: 1

   packagers
   semver
   testing
   compatibility
   api/modules
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _"extra" requirements:
 https://www.python.org/dev/peps/pep-0426/#extras-optional-dependencies
.. _conditional dependencies:
 https://www.python.org/dev/peps/pep-0426/#environment-markers
.. _distutils2: http://alexis.notmyidea.org/distutils2/setupcfg.html
.. _sphinx-apidoc man page: http://sphinx-doc.org/man/sphinx-apidoc.html
.. _Sphinx build configuration file: http://sphinx-doc.org/config.html
