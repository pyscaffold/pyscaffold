.. _extensions:

====================
Extending PyScaffold
====================

PyScaffold can be extended at runtime by other Python packages.
Therefore it is possible to change the default behavior of the ``putup``
command line tool without changing the PyScaffold code itself.


Creating an Extension
=====================

Extensions should implement a regular python function that receives as a single
argument a :class:`~pyscaffold.api.Scaffold` object.
This object is a representation of all the actions that will be performed by
the ``putup`` command, and contain the following properties:

:attr:`~pyscaffold.api.Scaffold.options` (*dict*)
  all PyScaffold options, including the ones parsed from command line;
:attr:`~pyscaffold.api.Scaffold.before_generate` (*list*)
  functions that will be executed **before** the generation of files;
:attr:`~pyscaffold.api.Scaffold.after_generate` (*list*)
  functions that will be executed **after** the generation of files;
:attr:`~pyscaffold.api.Scaffold.structure` (*dict*)
  directory tree representation as a (possibly nested) dictionary.
  The keys indicate each part of the path for the generated file,
  while the value indicate its contents.
:attr:`~pyscaffold.api.Scaffold.changed_structure` (*dict*)
  that is very similar to :attr:`~pyscaffold.api.Scaffold.structure`,
  but only stores files that actually change
  (this attribute is only assigned after project creation).

Additionally, the following methods are also available:

:obj:`~pyscaffold.api.Scaffold.merge_structure`
  deep merge the dictionary argument with the current representation of the
  to-be-generated directory tree.
:obj:`~pyscaffold.api.Scaffold.ensure_file`
  ensure a single file exists in the current representation of the tree,
  with the provided content, automatically creating the parent directories.
:obj:`~pyscaffold.api.Scaffold.reject_file`
  remove a file from the tree representation if the entire path exists.

The ``project`` and  ``package`` options can be used in order to ensure the
correct location of the files.

The following example illustrates a simple extension implementation:

.. code-block:: python

    MY_AWESOME_FILE = """\
    # -*- coding: utf-8 -*-
    from __future__ import print_function

    __author__ = "{author}"
    __copyright__ = "{author}"
    __license__ = "{license}"

    def awesome():
        return "Awesome!"
    """

    MY_AWESOME_TEST = """\
    import pytest
    from ${namespace_pkg}.awesome import awesome

    def test_awesome():
        assert awesome() == "Awesome!"
    """

    def extend_pyscaffold(scaffold):
        """Define extension behavior."""
        opts = scaffold.options

        # PyScaffold can run arbitrary functions before and after generating
        # the files.
        scaffold.before_generate.append(lambda _: print("Awesome Start"))
        scaffold.after_generate.append(lambda _: print("Awesome End"))

        # Extra files can be added to the PyScaffold structure.
        scaffold.merge_structure({
            opts['project']: {
                opts['package']: {
                    'awesome.py': MY_AWESOME_FILE.format(opts)
                    # When a leaf is a string, the content is written in the
                    # file path indicated by the dictionary keys.
                },
                'tests': {
                    'awesome_test.py': (
                        MY_AWESOME_TEST.format(opts),
                        scaffold.NO_OVERWRITE
                    )
                    # When a leaf is a tuple, the first element is used as
                    # content for the file, while the second element is used
                    # as the update rule for existing projects.
                }
            }
        })

        # Files can be directly added to the `structure` dict.
        scaffold.structure['.python-version'] = ('3.6.1', scaffold.NO_OVERWRITE)

        # The `ensure_file` method can be also used.
        for filename in opts['awesome_files']:
            scaffold.ensure_file(filename, content='AWESOME!',
                                 update_rule=scaffold.NO_CREATE
                                 path=[opts['project'], 'awesome'])

        # The `reject_file` can be used to avoid files being generated.
        del scaffold.reject_file('skeleton.py',
                                 path=[opts['project'], opts['package']])

Note that both :attr:`~pyscaffold.api.Scaffold.before_generate` and
:attr:`~pyscaffold.api.Scaffold.after_generate` hooks also should be
defined as a function of a single argument, a
:class:`~pyscffold.api.Scaffold` instance.


Activating Extensions
=====================

PyScaffold extensions are not activated by default. Instead, it is necessary
to add a CLI option to do it.
This is possible by setting up a `setuptools entry point
<http://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=dynamic#dynamic-discovery-of-services-and-plugins>`_.
under the ``pyscaffold.cli`` group.
This entry point should be a regular python function, that receives a
single ``parser`` argument (instance of the :class:`argparse.ArgumentParser`
class from standard lib).

After the command line arguments parsing, the extension function should be
stored under the ``extensions`` attribute (a list) of the :mod:`argparse`
generated object.

For example, assuming the aforementioned extension and the entry point
``{'pyscaffold.cli.awesome': 'awesome_ext:augment_cli'}``, the following
function may be implemented:

.. code-block:: python

    def augment_cli(parser):
        """Add an option to the ``putup`` command."""
        parser.add_argument('--with-awesome',
                            dest='extensions',
                            action='append_const',
                            const=extend_pyscaffold,
                            help='generate awesome extra files')

Note that, in this case, an option with the ``append_const`` action is created,
with ``extensions`` as ``dest`` and the extension function as ``const``.
Alternatively, when extra parameters are required, a custom
:class:`argparse.Action` subclass can be implemented, as indicated bellow:

.. code-block:: python

    import argparse

    class ActivateAwesome(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # First ensure the extension function is stored inside the
            # 'extensions' attribute:
            extensions = getattr(namespace, 'extensions', [])
            extensions.append(extend_pyscaffold)
            setattr(namespace, 'extensions', extensions)

            # Now the extra parameters can be stored
            setattr(namespace, self.dest, values)

    def augment_cli(parser):
        """Add an option to the ``putup`` command."""
        parser.add_argument('--with-awesome',
                            dest='awesome_args',
                            action=ActivateAwesome,
                            nargs=2,
                            help='generate awesome extra files')


Examples
========

Some options for the ``putup`` command are already implemented as extensions
and can be used as reference implementation:

.. toctree::
   :maxdepth: 2

   --with-cookiecutter <examples/cookiecutter-extension>
   --with-django <examples/django-extension>
   --with-pre-commit <examples/pre-commit-extension>
   --with-tox <examples/tox-extension>
   --with-travis <examples/travis-extension>
