=======
 Usage
=======

*pbr* is a *setuptools* plugin and so to use it you must use *setuptools* and
call ``setuptools.setup()``. While the normal *setuptools* facilities are
available, *pbr* makes it possible to express them through static data files.

.. _setup_py:

``setup.py``
------------

*pbr* only requires a minimal ``setup.py`` file compared to a standard
*setuptools* project. This is because most configuration is located in static
configuration files. This recommended minimal ``setup.py`` file should look
something like this::

    #!/usr/bin/env python

    from setuptools import setup

    setup(
        setup_requires=['pbr'],
        pbr=True,
    )

.. note::

   It is necessary to specify ``pbr=True`` to enabled *pbr* functionality.

.. note::

   While one can pass any arguments supported by setuptools to ``setup()``,
   any conflicting arguments supplied in ``setup.cfg`` will take precedence.

.. _setup_cfg:

``setup.cfg``
-------------

The ``setup.cfg`` file is an INI-like file that can mostly replace the
``setup.py`` file. It is similar to the ``setup.cfg`` file found in recent
versions of `setuptools`__. A simple sample can be found in *pbr*'s own
``setup.cfg`` (it uses its own machinery to install itself):

::

    [metadata]
    name = pbr
    author = OpenStack Foundation
    author-email = openstack-dev@lists.openstack.org
    summary = OpenStack's setup automation in a reusable form
    description-file = README.rst
    description-content-type = text/x-rst; charset=UTF-8
    home-page = https://launchpad.net/pbr
    project_urls =
        Bug Tracker = https://bugs.launchpad.net/pbr/
        Documentation = https://docs.openstack.org/pbr/
        Source Code = https://git.openstack.org/cgit/openstack-dev/pbr/
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

Recent versions of `setuptools`_ provide many of the same sections as *pbr*.
However, *pbr* does provide a number of additional sections:

- ``files``
- ``entry_points``
- ``backwards_compat``
- ``pbr``

In addition, there are some modifications to other sections:

- ``metadata``
- ``build_sphinx``

For all other sections, you should refer to either the `setuptools`_
documentation or the documentation of the package that provides the section,
such as the ``extract_mesages`` section provided by Babel__.

.. note::

   Comments may be used in ``setup.cfg``, however all comments should start
   with a ``#`` and may be on a single line, or in line, with at least one
   white space character immediately preceding the ``#``. Semicolons are not a
   supported comment delimiter. For instance::

       [section]
       # A comment at the start of a dedicated line
       key =
           value1 # An in line comment
           value2
           # A comment on a dedicated line
           value3

.. note::

   On Python 3 ``setup.cfg`` is explicitly read as UTF-8.  On Python 2 the
   encoding is dependent on the terminal encoding.

__ http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
__ http://babel.pocoo.org/en/latest/setup.html

``files``
~~~~~~~~~

The ``files`` section defines the install location of files in the package
using three fundamental keys: ``packages``, ``namespace_packages``, and
``data_files``.

``packages``
  A list of top-level packages that should be installed. The behavior of
  packages is similar to ``setuptools.find_packages`` in that it recurses the
  Python package hierarchy below the given top level and installs all of it. If
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
  directories. Additionally, *pbr* supports a simple file globbing syntax for
  installing entire directory structures. For example::

      [files]
      data_files =
          etc/pbr = etc/pbr/*
          etc/neutron =
              etc/api-paste.ini
              etc/dhcp-agent.ini
          etc/init.d = neutron.init

  This will result in ``/etc/neutron`` containing ``api-paste.ini`` and
  ``dhcp-agent.ini``, both of which *pbr* will expect to find in the ``etc``
  directory in the root of the source tree. Additionally, ``neutron.init`` from
  that directory will be installed in ``/etc/init.d``. All of the files and
  directories located under ``etc/pbr`` in the source tree will be installed
  into ``/etc/pbr``.

  Note that this behavior is relative to the effective root of the environment
  into which the packages are installed, so depending on available permissions
  this could be the actual system-wide ``/etc`` directory or just a top-level
  ``etc`` subdirectory of a *virtualenv*.

``entry_points``
~~~~~~~~~~~~~~~~

The ``entry_points`` section defines entry points for generated console scripts
and Python libraries. This is actually provided by *setuptools* but is
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

Will cause a console script called *pbr* to be installed that executes the
``main`` function found in ``pbr.cmd``. Additionally, two entry points will be
installed for ``pbr.config.drivers``, one called ``plain`` which maps to the
``Plain`` class in ``pbr.cfg.driver`` and one called ``fancy`` which maps to
the ``Fancy`` class in ``pbr.cfg.driver``.

``backwards_compat``
~~~~~~~~~~~~~~~~~~~~~

.. todo:: Describe this section

.. _pbr-setup-cfg:

``pbr``
~~~~~~~

The ``pbr`` section controls *pbr*-specific options and behaviours.

``autodoc_tree_index_modules``

  A boolean option controlling whether *pbr* should generate an index of
  modules using ``sphinx-apidoc``. By default, all files except ``setup.py``
  are included, but this can be overridden using the ``autodoc_tree_excludes``
  option.

``autodoc_tree_excludes``

  A list of modules to exclude when building documentation using
  ``sphinx-apidoc``. Defaults to ``[setup.py]``. Refer to the
  `sphinx-apidoc man page`__ for more information.

__ http://sphinx-doc.org/man/sphinx-apidoc.html

``autodoc_index_modules``

  A boolean option controlling whether *pbr* should itself generates
  documentation for Python modules of the project. By default, all found Python
  modules are included; some of them can be excluded by listing them in
  ``autodoc_exclude_modules``.

``autodoc_exclude_modules``

  A list of modules to exclude when building module documentation using *pbr*.
  *fnmatch* style pattern (e.g. ``myapp.tests.*``) can be used.

``api_doc_dir``

  A subdirectory inside the ``build_sphinx.source_dir`` where auto-generated
  API documentation should be written, if ``autodoc_index_modules`` is set to
  True. Defaults to ``"api"``.

.. note::

   When using ``autodoc_tree_excludes`` or ``autodoc_index_modules`` you may
   also need to set ``exclude_patterns`` in your Sphinx configuration file
   (generally found at ``doc/source/conf.py`` in most OpenStack projects)
   otherwise Sphinx may complain about documents that are not in a toctree.
   This is especially true if the ``[sphinx_build] warning-is-error`` option is
   set. See the `Sphinx build configuration file`__ documentation for more
   information on configuring Sphinx.

__ http://sphinx-doc.org/config.html

.. versionchanged:: 2.0

   The ``pbr`` section used to take a ``warnerrors`` option that would enable
   the ``-W`` (Turn warnings into errors.) option when building Sphinx. This
   feature was broken in 1.10 and was removed in pbr 2.0 in favour of the
   ``[build_sphinx] warning-is-error`` provided in Sphinx 1.5+.

``metadata``
~~~~~~~~~~~~

.. todo:: Describe this section

.. _build_sphinx-setup-cfg:

``build_sphinx``
~~~~~~~~~~~~~~~~

.. versionchanged:: 3.0

   The ``build_sphinx`` plugin used to default to building both HTML and man
   page output. This is no longer the case, and you should explicitly set
   ``builders`` to ``html man`` if you wish to retain this behavior.

The ``build_sphinx`` section is a version of the ``build_sphinx`` *setuptools*
plugin provided with Sphinx. This plugin extends the original plugin to add the
following:

- Automatic generation of module documentation using the ``sphinx-apidoc`` tool

- Automatic configuration of the ``project``, ``version`` and ``release``
  settings using information from *pbr* itself

- Support for multiple builders using the ``builders`` configuration option

  .. note::

     Only applies to Sphinx < 1.6. See documentation on ``builders`` below.

The version of ``build_sphinx`` provided by *pbr* provides a single additional
option.

``builders``
  A comma separated list of builders to run. For example, to build both HTML
  and man page documentation, you would define the following in your
  ``setup.cfg``:

  .. code-block:: ini

      [build_sphinx]
      builders = html,man
      source-dir = doc/source
      build-dir = doc/build
      all-files = 1
      warning-is-error = 1

  .. deprecated:: 3.2.0

     Sphinx 1.6+ adds support for specifying multiple builders in the default
     ``builder`` option. You should use this option instead. Refer to the
     `Sphinx documentation`_ for more information.

For information on the remaining options, refer to the `Sphinx documentation`_.
In addition, the ``autodoc_index_modules``, ``autodoc_tree_index_modules``,
``autodoc_exclude_modules`` and ``autodoc_tree_excludes`` options :ref:`in the
pbr section <pbr-setup-cfg>` will affect the output of the automatic module
documentation generation.

.. _Sphinx documentation: http://www.sphinx-doc.org/en/stable/setuptools.html

Requirements
------------

Requirements files are used in place of the ``install_requires`` and
``extras_require`` attributes. Requirement files should be given one of the
below names. This order is also the order that the requirements are tried in
(where ``N`` is the Python major version number used to install the package):

* ``requirements-pyN.txt``
* ``tools/pip-requires-py3``
* ``requirements.txt``
* ``tools/pip-requires``

Only the first file found is used to install the list of packages it contains.

.. note::

   The ``requirements-pyN.txt`` file is deprecated - ``requirements.txt``
   should be universal. You can use `Environment markers`_ for this purpose.

.. _extra-requirements:

Extra requirements
~~~~~~~~~~~~~~~~~~

Groups of optional dependencies, or `"extra" requirements`__, can be described
in your ``setup.cfg``, rather than needing to be added to ``setup.py``. An
example (which also demonstrates the use of environment markers) is shown
below.

__ https://www.python.org/dev/peps/pep-0426/#extras-optional-dependencies

Environment markers
~~~~~~~~~~~~~~~~~~~

Environment markers are `conditional dependencies`__ which can be added to the
requirements (or to a group of extra requirements) automatically, depending on
the environment the installer is running in. They can be added to requirements
in the requirements file, or to extras defined in ``setup.cfg``, but the format
is slightly different for each.

For ``requirements.txt``::

    argparse; python_version=='2.6'

This will result in the package depending on ``argparse`` only if it's being
installed into Python 2.6.

For extras specified in ``setup.cfg``, add an ``extras`` section. For instance,
to create two groups of extra requirements with additional constraints on the
environment, you can use::

    [extras]
    security =
        aleph
        bet:python_version=='3.2'
        gimel:python_version=='2.7'
    testing =
        quux:python_version=='2.7'

__ https://www.python.org/dev/peps/pep-0426/#environment-markers

Testing
-------

.. deprecated:: 4.0

As described in :doc:`/user/features`, *pbr* may override the ``test`` command
depending on the test runner used.

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

The argument ``--coverage`` will set ``PYTHON`` to ``coverage run`` to produce
a coverage report.  ``--coverage-package-name`` can be used to modify or narrow
the packages traced.

.. _setuptools: http://www.sphinx-doc.org/en/stable/setuptools.html
