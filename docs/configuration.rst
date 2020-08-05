.. _configuration:

=============
Configuration
=============

Package Configuration
=====================

Projects set up with PyScaffold rely on `setuptools`_, and therefore can be
easy configured/customised via ``setup.cfg``. Check out the example below:

.. literalinclude:: ./example_setup.cfg
    :language: ini

You might also want to have a look on `pyproject.toml`_ for specifying
dependencies required during the build:

.. literalinclude:: ../src/pyscaffold/templates/pyproject_toml.template
    :language: toml


.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _pyproject.toml: https://setuptools.readthedocs.io/en/latest/build_meta.html


.. _default-cfg:

PyScaffold's Own Configuration
==============================

PyScaffold also allows you to save your favourite configuration to a file that
will be automatically read every time you run ``putup``, this way you can avoid
always retyping the same command line options.

The locations of the configuration files vary slightly across platforms, but in
general the following rule applies:

- Linux: ``$XDG_CONFIG_HOME/pyscaffold/default.cfg`` with fallback to ``~/.config/pyscaffold/default.cfg``
- OSX: ``~/Library/Preferences/pyscaffold/default.cfg``
- Windows(≥7): ``%APPDATA%\pyscaffold\pyscaffold\default.cfg``

The file format resembles the ``setup.cfg`` generated automatically by
PyScaffold, but with only the ``metadata`` and ``pyscaffold`` sections, for
example:

.. code-block:: ini

    [metadata]
    author = John Doe
    author-email = john.joe@gmail.com
    license = mozilla

    [pyscaffold]
    extensions =
        tox
        travis
        pre-commit

With this file in place, typing only::

    $ putup myproj

will have the same effect as if you had typed::

    $ putup --license mozilla --tox --travis --pre-commit myproj


.. note::

    Only the following options are allowed in the config file:

    - **metadata** section: ``author``, ``author-email`` and ``license``
    - **pyscaffold** section: ``extensions`` (and associated opts)

    Options associated with extensions are the ones prefixed by an extension name.


To prevent PyScaffold from reading an existing config file, you can pass the
``--no-config`` option in the CLI. You can also save the given options when
creating a new project with the ``--save-config`` option. Finally, to read the
configurations from a location other then the default, use the ``--config
PATH`` option.


.. warning::

    *Experimental Feature* - We are still evaluating how this new and exciting
    feature will work, so its API (including file format) is not considered
    stable and might change between minor versions.
