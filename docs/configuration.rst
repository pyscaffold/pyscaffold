.. _configuration:

=============
Configuration
=============

Projects set up with PyScaffold feature an easy package configuration with
``setup.cfg``. Check out the example below as well as the documentation of
`setuptools`_.

.. literalinclude:: ./example_setup.cfg
    :language: Ini

.. _setuptools: http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files


.. _default-cfg:

Reusing Presets
===============

PyScaffold also allows you to save your favourite CLI parameters to a file that
will be automatically read every time you run ``putup``, this way you can avoid
always retyping the same command line options.

The locations of the preset files vary slightly across platforms, but in
general the following rule applies:

- Linux: ``$XDG_CONFIG_HOME/pyscaffold/default.cfg`` with fallback to ``~/.config/pyscaffold/default.cfg``
- OSX: ``~/Library/Preferences/pyscaffold/default.cfg``
- Windows(≥7): ``C:\Users\<username>\AppData\Local\pyscaffold\pyscaffold\default.cfg``

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

With this preset file in place, typing only::

    $ putup myproj

will have the same effect as if you had typed::

    $ putup --license mozilla --tox --travis --pre-commit myproj


.. warning::

    *Experimental Feature* - We are still evaluating how this new and exciting
    feature will work, so its API (including file format) is not considered
    stable and might change between minor versions.
