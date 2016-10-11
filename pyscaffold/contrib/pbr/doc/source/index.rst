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

There are a number of sections in these documents. These are:

* metadata
* files
* entry_points
* pbr

files
~~~~~

The ``files`` section defines the install location of files in the package
using three fundamental keys: ``packages``, ``namespace_packages``, and
``data_files``.

``packages`` is a list of top-level packages that should be installed. The
behavior of packages is similar to ``setuptools.find_packages`` in that it
recurses the python package hierarchy below the given top level and installs
all of it. If ``packages`` is not specified, it defaults to the value of the
``name`` field given in the ``[metadata]`` section.

``namespace_packages`` is the same, but is a list of packages that provide
namespace packages.

``data_files`` lists files to be installed. The format is an indented block
that contains key value pairs which specify target directory and source file
to install there. More than one source file for a directory may be indicated
with a further indented list. Source files are stripped of leading directories.
Additionally, `pbr` supports a simple file globbing syntax for installing
entire directory structures, thus::

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
this could be the actual system-wide `/etc` directory or just a top-level `etc`
subdirectory of a virtualenv.

entry_points
~~~~~~~~~~~~

The `entry_points` section defines entry points for generated console scripts
and python libraries.

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

pbr
~~~

The pbr section controls pbr specific options and behaviours.

The ``autodoc_tree_index_modules`` is a boolean option controlling whether pbr
should generate an index of modules using ``sphinx-apidoc``. By default,
`setup.py` is excluded. The list of excluded modules can be specified with the
``autodoc_tree_excludes`` option. See the `sphinx-apidoc man page`_ for more
information.

The ``autodoc_index_modules`` is a boolean option controlling whether `pbr`
should itself generates documentation for Python modules of the project. By
default, all found Python modules are included; some of them can be excluded
by listing them in ``autodoc_exclude_modules``. This list of modules can
contains `fnmatch` style pattern (e.g. `myapp.tests.*`) to exclude some modules.

The ``warnerrors`` boolean option is used to tell Sphinx builders to treat
warnings as errors which will cause sphinx-build to fail if it encounters
warnings. This is generally useful to ensure your documentation stays clean
once you have a good docs build.

.. note::

   When using ``autodoc_tree_excludes`` or ``autodoc_index_modules`` you may
   also need to set ``exclude_patterns`` in your Sphinx configuration file
   (generally found at `doc/source/conf.py` in most OpenStack projects)
   otherwise Sphinx may complain about documents that are not in a toctree.
   This is especially true if the ``warnerrors=True`` option is set. See the
   `Sphinx build configuration file`_ documentation for more information on
   configuring
   Sphinx.

Comments
~~~~~~~~

Comments may be used in `setup.cfg`, however all comments should start with a
`#` and may be on a single line, or in line, with at least one white space
character immediately preceding the `#`. Semicolons are not a supported comment
delimiter. For instance::

    [section]
    # A comment at the start of a dedicated line
    key =
        value1 # An in line comment
        value2
        # A comment on a dedicated line
        value3

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

For extras specifed in `setup.cfg`, add an ``extras`` section. For instance,
to create two groups of extra requirements with additional constraints on the
environment, you can use::

    [extras]
    security =
        aleph
        bet:python_version=='3.2'
        gimel:python_version=='2.7'
    testing =
        quux:python_version=='2.7'

Additional Docs
===============

.. toctree::
   :maxdepth: 1

   packagers
   semver
   testing
   compatibility

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
