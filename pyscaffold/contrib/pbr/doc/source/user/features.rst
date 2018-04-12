==========
 Features
==========

To understand what *pbr* can do for you, it's probably best to look at two
projects: one using pure *setuptools*, and another using *pbr*. First, let's
look at the *setuptools* project.

.. code-block:: none

   $ tree -L 1
   .
   ├── AUTHORS
   ├── CHANGES
   ├── LICENSE
   ├── MANIFEST.in
   ├── README.rst
   ├── requirements.txt
   ├── setup.cfg
   ├── setup.py
   └── somepackage

   $ cat setup.py
   setuptools.setup(
       name='mypackage',
       version='1.0.0',
       description='A short description',
       long_description="""A much longer description...""",
       author="John Doe",
       author_email='john.doe@example.com',
       license='BSD',
   )

Here's a similar package using *pbr*:

.. code-block:: none

   $ tree -L 1
   .
   ├── LICENSE
   ├── README.rst
   ├── setup.cfg
   ├── setup.py
   └── somepackage

   $ cat setup.py
   setuptools.setup(
       pbr=True
   )

   $ cat setup.cfg
   [metadata]
   name = mypackage
   description = A short description
   description-file = README.rst
   author = John Doe
   author-email = john.doe@example.com
   license = BSD

From this, we note a couple of the main features of *pbr*:

- Extensive use of ``setup.cfg`` for configuration
- Automatic package metadata generation (``version``)
- Automatic metadata file generation (``AUTHOR``, ``ChangeLog``,
  ``MANIFEST.in``)

In addition, there are other things that you don't see here but which *pbr*
will do for you:

- Helpful extensions to *setuptools* commands

setup.cfg
---------

.. admonition:: Summary

    *pbr* uses ``setup.cfg`` for all configuration, though ``setup.py`` is
    still required.

One of the main features of *distutils2* was the use of a ``setup.cfg``
INI-style configuration file. This was used to define a package's metadata and
other options that were normally supplied to the ``setup()`` function.

Recent versions of `setuptools`__ have implemented some of this support, but
*pbr* still allows for the definition of the following sections in
``setup.cfg``:

- ``files``
- ``entry_points``
- ``backwards_compat``

For more information on these sections, refer to :doc:`/user/using`.

__ https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files

Package Metadata
----------------

.. admonition:: Summary

    *pbr* removes the need to define a lot of configuration in either
    ``setup.py`` or ``setup.cfg`` by extracting this information from Git.

Version
~~~~~~~

.. admonition:: Summary

    *pbr* will automatically configure your version for you by parsing
    semantically-versioned Git tags.

Versions can be managed two ways - *post-versioning* and *pre-versioning*.
*Post-versioning* is the default while *pre-versioning* is enabled by setting
``version`` in the ``setup.cfg`` ``metadata`` section. In both cases the actual
version strings are inferred from Git.

If the currently checked out revision is tagged, that tag is used as
the version.

If the currently checked out revision is not tagged, then we take the
last tagged version number and increment it to get a minimum target
version.

.. note::

   *pbr* supports both bare version tag (e.g. ``0.1.0``) and version prefixed
   with ``v`` or ``V`` (e.g. ``v0.1.0``)

We then walk Git history back to the last release. Within each commit we look
for a ``Sem-Ver:`` pseudo header and, if found, parse it looking for keywords.
Unknown symbols are not an error (so that folk can't wedge *pbr* or break their
tree), but we will emit an info-level warning message. The following symbols
are recognized:

- ``feature``
- ``api-break``
- ``deprecation``
- ``bugfix``

A missing ``Sem-Ver`` line is equivalent to ``Sem-Ver: bugfix``. The ``bugfix``
symbol causes a patch level increment to the version. The ``feature`` and
``deprecation`` symbols cause a minor version increment. The ``api-break``
symbol causes a major version increment.

If *post-versioning* is in use, we use the resulting version number as the target
version.

If *pre-versioning* is in use, we check that the version set in the metadata
section of ``setup.cfg`` is greater than the version we infer using the above
method. If the inferred version is greater than the *pre-versioning* value we
raise an error, otherwise we use the version from ``setup.cfg`` as the target.

We then generate dev version strings based on the commits since the last
release and include the current Git SHA to disambiguate multiple dev versions
with the same number of commits since the release.

.. note::

   *pbr* expects Git tags to be signed for use in calculating versions.

The versions are expected to be compliant with :doc:`semver`.

The ``version.SemanticVersion`` class can be used to query versions of a
package and present it in various forms - ``debian_version()``,
``release_string()``, ``rpm_string()``, ``version_string()``, or
``version_tuple()``.

Long Description
~~~~~~~~~~~~~~~~

.. admonition:: Summary

    *pbr* can extract the contents of a ``README`` and use this as your long
    description

There is no need to maintain two long descriptions and your ``README`` file is
probably a good long_description. So we'll just inject the contents of your
``README.rst``, ``README.txt`` or ``README`` file into your empty
``long_description``.

You can also specify the exact file you want to use using the
``description-file`` parameter.

Requirements
~~~~~~~~~~~~

.. admonition:: Summary

    *pbr* will extract requirements from ``requirements.txt`` files and
    automatically populate the ``install_requires``, ``tests_require`` and
    ``dependency_links`` arguments to ``setup`` with them.

You may not have noticed, but there are differences in how pip
``requirements.txt`` files work and how *setuptools* wants to be told about
requirements. The *pip* way is nicer because it sure does make it easier to
populate a *virtualenv* for testing or to just install everything you need.
Duplicating the information, though, is super lame. To solve this issue, *pbr*
will let you use ``requirements.txt``-format files to describe the requirements
for your project and will then parse these files, split them up appropriately,
and inject them into the ``install_requires``, ``tests_require`` and/or
``dependency_links`` arguments to ``setup``. Voila!

You can also have a requirement file for each specific major version of Python.
If you want to have a different package list for Python 3 then just drop a
``requirements-py3.txt`` and it will be used instead.

Finally, it is possible to specify groups of optional dependencies, or
:ref:`"extra" requirements <extra-requirements>`, in your ``setup.cfg`` rather
than ``setup.py``.

Automatic File Generation
-------------------------

.. admonition:: Summary

    *pbr* can automatically generate a couple of files, which would normally
    have to be maintained manually, by using Git data.

AUTHORS, ChangeLog
~~~~~~~~~~~~~~~~~~

.. admonition:: Summary

    *pbr* will automatically generate an ``AUTHORS`` and a ``ChangeLog`` file
    using Git logs.

Why keep an ``AUTHORS`` or a ``ChangeLog`` file when Git already has all of the
information you need? ``AUTHORS`` generation supports filtering/combining based
on a standard ``.mailmap`` file.

Manifest
~~~~~~~~

.. admonition:: Summary

    *pbr* will automatically generate a ``MANIFEST.in`` file based on the files
    Git is tracking.

Just like ``AUTHORS`` and ``ChangeLog``, why keep a list of files you wish to
include when you can find many of these in Git. ``MANIFEST.in`` generation
ensures almost all files stored in Git, with the exception of ``.gitignore``,
``.gitreview`` and ``.pyc`` files, are automatically included in your
distribution. In addition, the generated ``AUTHORS`` and ``ChangeLog`` files
are also included. In many cases, this removes the need for an explicit
``MANIFEST.in`` file, though one can be provided to exclude files that are
tracked via Git but which should not be included in the final release, such as
test files.

.. note::

   ``MANIFEST.in`` files have no effect on binary distributions such as wheels.
   Refer to the `Python packaging tutorial`__ for more information.

__ https://packaging.python.org/tutorials/distributing-packages/#manifest-in

Setup Commands
--------------

``build_sphinx``
~~~~~~~~~~~~~~~~

.. admonition:: Summary

    *pbr* will override the Sphinx ``build_sphinx`` command to use
    *pbr*-provided package metadata and automatically generate API
    documentation.

Sphinx can produce auto documentation indexes based on signatures and
docstrings of your project but you have to give it index files to tell it to
*autodoc* each module: that's kind of repetitive and boring. *pbr* will scan
your project, find all of your modules, and generate all of the stub files for
you.

In addition, Sphinx documentation setups are altered to have several pieces of
information that are known to ``setup.py`` injected into the Sphinx config.

See the :ref:`pbr-setup-cfg` section of the configuration file for
details on configuring your project for *autodoc*.

``test``
~~~~~~~~

.. admonition:: Summary

    *pbr* will automatically alias the ``test`` command to use the testing tool
    of your choice.

.. deprecated:: 4.0

*pbr* overrides the *setuptools* ``test`` command if using `testrepository`__
or `nose`__ (deprecated).

- *pbr* will check for a ``.testr.conf`` file. If this exists and
  *testrepository* is installed, the ``test`` command will alias the *testr*
  test runner. If this is not the case...

  .. note::

    This is separate to ``setup.py testr`` (note the extra ``r``) which is
    provided directly by the ``testrepository`` package. Be careful as there is
    some overlap of command arguments.

- *pbr* will check if ``[nosetests]`` is defined in ``setup.cfg``. If this
  exists and *nose* is installed, the ``test`` command will alias the *nose*
  runner. If this is not the case...

- In other cases no override will be installed and the ``test`` command will
  revert to the `setuptools default`__.

__ https://testrepository.readthedocs.io/en/latest/
__ https://nose.readthedocs.io/en/latest/
__ https://setuptools.readthedocs.io/en/latest/setuptools.html#test-build-package-and-run-a-unittest-suite
