setuptools_scm
===============

:code:`setuptools_scm` handles managing your python package versions
in scm metadata instead of declaring them as the version argument
or in a scm managed file.

It also handles file finders for the supported scm's.

.. image:: https://travis-ci.org/pypa/setuptools_scm.svg?branch=master
    :target: https://travis-ci.org/pypa/setuptools_scm

Setup.py usage
--------------

To use setuptools_scm just modify your project's setup.py file like this:

1. Add :code:`'setuptools_scm'` to the :code:`setup_requires` parameter
2. Add the :code:`use_scm_version` parameter and set it to ``True``


   E.g.:

   .. code:: python

       from setuptools import setup
       setup(
           ...,
           use_scm_version=True,
           setup_requires=['setuptools_scm'],
           ...,
       )


Programmatic usage
------------------

In order to use setuptools_scm for sphinx config, assuming the sphinx conf
is one directory deeper than the project's root, use:

.. code:: python

    from setuptools_scm import get_version
    version = get_version(root='..', relative_to=__file__)


Notable Plugins
----------------

`setuptools_scm_git_archive <https://pypi.python.org/pypi/setuptools_scm_git_archive>`_
provides partial support for obtaining versions from git archives
that belong to tagged versions. The only reason for not including
it in setuptools-scm itself is git/github not supporting
sufficient metadata for untagged/followup commits,
which is preventing a consistent UX.


Default versioning scheme
--------------------------

In the standard configuration setuptools_scm takes a look at 3 things:

1. latest tag (with a version number)
2. the distance to this tag (e.g. number of revisions since latest tag)
3. workdir state (e.g. uncommitted changes since latest tag)

and uses roughly the following logic to render the version:

:code:`no distance and clean`:
    :code:`{tag}`
:code:`distance and clean`:
    :code:`{next_version}.dev{distance}+n{revision hash}`
:code:`no distance and not clean`:
    :code:`{tag}+dYYYMMMDD`
:code:`distance and not clean`:
    :code:`{next_version}.dev{distance}+n{revision hash}.dYYYMMMDD`

The next version is calculated by adding ``1`` to the last numeric component
of the tag.

Semantic Versioning (SemVer)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Due to the default behavior it's necessary to always include a
patch version (the ``3`` in ``1.2.3``), or else the automatic guessing
will increment the wrong part of the semver (e.g. tag ``2.0`` results in
``2.1.devX`` instead of ``2.0.1.devX``). So please make sure to tag
accordingly.

.. note::

    Future versions of setuptools_scm will switch to
    `SemVer <http://semver.org/>`_ by default hiding the the old behavior
    as an configurable option.


Builtin mechanisms for obtaining version numbers
--------------------------------------------------

1. the scm itself (git/hg)
2. :code:`.hg_archival` files (mercurial archives)
3. PKG-INFO

.. note::

    git archives are not supported due to git shortcomings


Configuration Parameters
------------------------------

In order to configure the way ``use_scm_version`` works you can provide
a mapping with options instead of simple boolean value.

The Currently supported configuration keys are:

:root:
    cwd relative path to use for finding the scm root, defaults to :code:`.`

:version_scheme:
    configures how the local version number is constructed.
    either an entrypoint name or a callable

:local_scheme:
    configures how the local component of the version is constructed
    either an entrypoint name or a callable
:write_to:
    declares a text file or python file which is replaced with a file
    containing the current version.
    its ideal or creating a version.py file within the package

    .. warning::

      only :code:`*.py` and :code:`*.txt` have builtin templates,
      for other extensions it is necessary
      to provide a :code:`write_to_template`
:write_to_template:
    a newstyle format string thats given the current version as
    the :code:`version` keyword argument for formatting

:relative_to:
    a file from which root may be resolved. typically called by a
    script or module that is not
    in the root of the repository to direct setuptools_scm to the
    root of the repository by supplying ``__file__``.

:parse:
  a function that will be used instead of the discovered scm for parsing the version,
  use with caution, this is a expert function and you should be closely familiar
  with the setuptools_scm internals to use it


To use setuptools_scm in other Python code you can use the
``get_version`` function:

.. code:: python

    from setuptools_scm import get_version
    my_version = get_version()

It optionally accepts the keys of the ``use_scm_version`` parameter as
keyword arguments.


Environment Variables
---------------------

:SETUPTOOLS_SCM_PRETEND_VERSION:
  when defined and not empty,
  its used as the primary source for the version number
  in which case it will be a unparsed string


Extending setuptools_scm
------------------------

setuptools_scm ships with a few setuptools entrypoints based hooks to extend
its default capabilities.

Adding a new SCM
~~~~~~~~~~~~~~~~

setuptools_scm provides 2 entrypoints for adding new SCMs

``setuptools_scm.parse_scm``
    A function used to parse the metadata of the current workdir
    using the name of the control directory/file of your SCM as the
    entrypoint's name. E.g. for the built-in entrypoint for git the
    entrypoint is named :code:`.git` and references
    :code:`'setuptools_scm.git:parse'`.

    The return value MUST be a :code:`setuptools.version.ScmVersion` instance
    created by the function :code:`setuptools_scm.version:meta`.

``setuptools_scm.files_command``
    Either a string containing a shell command that prints all SCM managed
    files in its current working directory or a callable, that given a
    pathname will return that list.

    Also use then name of your SCM control directory as name of the entrypoint.

Version number construction
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``setuptools_scm.version_scheme``
    Configures how the version number is constructed given a
    :code:`setuptools.version.ScmVersion` instance and should return a string
    representing the version.

    Available implementations:

    :guess-next-dev: automatically guesses the next development version (default)
    :post-release: generates post release versions (adds :code:`postN`)

``setuptools_scm.local_scheme``
    Configures how the local part of a version is rendered given a
    :code:`setuptools.version.ScmVersion` instance and should return a string
    representing the local version.

    Available implementations:

    :node-and-date: adds the node on dev versions and the date on dirty
                    workdir (default)
    :dirty-tag: adds :code:`+dirty` if the current workdir has changes


Importing in setup.py
~~~~~~~~~~~~~~~~~~~~~

To support usage in :code:`setup.py` passing a callable into use_scm_version
is supported.

Within that callable, setuptools_scm is available for import.
The callable must return the configuration.


.. code:: python

    def myversion():
        from setuptools_scm.version import dirty_tag
        def clean_scheme(version):
            if not version.dirty:
                return '+clean'
            else:
                return dirty_tag(version)

        return {'local_scheme': clean_scheme}


Code of Conduct
---------------

Everyone interacting in the setuptools_scm project's codebases, issue trackers,
chat rooms, and mailing lists is expected to follow the
`PyPA Code of Conduct`_.

.. _PyPA Code of Conduct: https://www.pypa.io/en/latest/code-of-conduct/
