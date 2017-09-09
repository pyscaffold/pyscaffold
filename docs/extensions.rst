.. _extensions:

====================
Extending PyScaffold
====================

PyScaffold is carefully designed to cover the essentials of authoring and
distributing Python packages. Most of time, tweaking ``putup`` options is
enough to ensure proper configuration of a project. For some basic
customization, an additional :ref:`Cookiecutter template
<cookiecutter-integration>` can yet be used.
However, for advanced use cases a deeper level of programmability may be
required.

Fortunately, PyScaffold can be extended at runtime by other Python packages.
Therefore it is possible to change the behavior of the ``putup`` command line
tool without changing the PyScaffold code itself. In order to explain how this
mechanism works, the following sections define a few important concepts and
present a comprehensive guide about how to create custom extensions.


.. _coreconcepts:

Project Structure Representation
================================

Each Python package project is internally represented by PyScaffold as a tree
data structure, that directly relates to a directory entry in the file system.
This tree is implemented as a simple (and possibly nested) :obj:`dict` in which
keys indicate the path where files will be generated, while values indicate
their content. For instance, the following dict::

    {
        'project': {
            'folder': {
                'file.txt': 'Hello World!',
                'another-folder': {'empty-file.txt': ''}
            }
        }
    }

represents a ``project/folder`` directory in the file system containing two
entries. The first entry is a file named `file.txt` with content `Hello World!`
while the second entry is a sub-directory named `another-folder`. In turn,
`another-folder` contains an empty file named `empty-file.txt`.

Additionally, tuple values are also allowed in order to specify some useful
metadata.  In this case, the first element of the tuple is the file content.
For example, the dict::

    {
        'project': {
            'namespace': {
                'module.py': ('print("Hello World!")', helpers.NO_OVERWRITE)
            }
        }
    }

represents a ``project/namespace/module.py`` file with content
``print("Hello World!")``, that will not be overwritten if already exists.

This tree representation is often referred in this document as **project
structure** or simply **structure**.


Scaffold Actions
================

PyScaffold organizes the generation of a project into a series of steps with
well defined purposes. Each step is called **action** and is implemented as a
simple function that receives two arguments: a project structure and a dict
with options (some of them parsed from command line arguments, other from
default values).

An action **MUST** return a tuple also composed by a project structure and a
dict with options. The return values, thus, are usually modified versions
of the input arguments. Additionally an action can also have side effects, like
creating directories or adding files to version control. The following
pseudo-code illustrates a basic action:

.. code-block:: python

    def action(project_structure, options):
        new_struct, new_opts = modify(project_structure, options)
        some_side_effect()
        return (new_struct, new_opts)

The output of each action is used as the input of the subsequent action, and
initially the structure argument is just an empty dict. Each action is uniquely
identified by a string in the format ``<module name>:<function name>``,
similarly to the convention used for `setuptools entry points
<http://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=dynamic#dynamic-discovery-of-services-and-plugins>`_.
For example, if an action is defined in the ``action`` function of the
``extras.py`` file that is part of the ``pyscaffold.contrib`` project,
the **action identifier** is ``pyscaffold.contrib.extras:action``.

By default, the sequence of actions taken by PyScaffold is:

#. :obj:`pyscaffold.api:get_default_options <pyscaffold.api.get_default_options>`
#. :obj:`pyscaffold.api:verify_options_consistency <pyscaffold.api.verify_options_consistency>`
#. :obj:`pyscaffold.structure:define_structure <pyscaffold.structure.define_structure>`
#. :obj:`pyscaffold.structure:apply_update_rules <pyscaffold.structure.apply_update_rules>`
#. :obj:`pyscaffold.structure:create_structure <pyscaffold.structure.create_structure>`
#. :obj:`pyscaffold.api:init_git <pyscaffold.api.init_git>`

The project structure is usually empty until **define_structure**.
This action just loads the in-memory dict representation, that is only written
to disk by the **create_structure** action.

Note that, this sequence varies according to the command line options.
To retrieve an updated list, please use ``putup --list-actions`` or
``putup --dry-run``.


What are Extensions?
====================

From the standpoint of PyScaffold, extensions are composed by a group of
functions that can be used to inject actions at arbitrary positions in the
aforementioned list. Furthermore, extensions can also remove actions.


Creating an Extension
=====================

In order to create an extension it is necessary to implement a regular python
function that:

- receives a list of actions as first argument,
- receives a :mod:`namespace object <pyscaffold.api.helpers>` containing some
  helper methods as second argument,
- registers custom actions that will be called later and
- returns a modified version of the list of actions.

The following pseudo-code highlights a typical definition of such kind of
functions:

.. code-block:: python

    def extend_scaffold(actions, helpers):
        """Register custom actions that apply extension behavior."""

        # ... define `start_hook`, `finish_hook` and `define_awesome_files`
        #     functions

        actions = helpers.register(actions, start_hook, before='create_structure')
        actions = helpers.register(actions, finish_hook, after='create_structure')
        actions = helpers.register(actions, define_awesome_files)
        actions = helpers.unregister(actions, 'init_git')

        return actions

Action List Helper Methods
--------------------------

As implied by the previous example, the :mod:`~pyscaffold.api.helpers` argument
provides a series of useful functions and makes it easier to manipulate the
action list, by using :obj:`~pyscaffold.api.helpers.register` and
:obj:`~pyscaffold.api.helpers.unregister`.

Since the action order is relevant, the first function accepts special keyword
arguments (``before`` and ``after``) that should be used to place the extension
actions precisely among the default actions.  The value of these arguments can
be presented in 2 different forms::

    helpers.register(actions, hook1, before='define_structure')
    helpers.register(actions, hook2, after='pyscaffold.structure:create_structure')

The first form uses as a position reference the first action with a matching
name, regardless of the module. Accordingly, the second form tries to find an
action that matches both the given name and module. When no reference is given,
:obj:`~pyscaffold.api.helpers.register` assumes as default position
``after='pyscaffold.structure:define_structure'``.  This position is special
since most extensions are expected to create additional files inside the
project. Therefore, it is possible to easily amend the project structure before
it is materialized by ``create_structure``.

The :obj:`~pyscaffold.api.helpers.unregister` function accepts as second
argument a position reference which can similarly present the module name::

        helpers.unregister(actions, 'init_git')
        helpers.unregister(actions, 'pyscaffold.api:init_git')

.. note::

    These functions **DO NOT** modify the actions list, instead they return a
    new list with the changes applied.


Structure Helper Methods
------------------------

PyScaffold also provides extra facilities to manipulate the project structure.
The following functions are accessible through the
:mod:`~pyscaffold.api.helpers` argument:

- :obj:`~pyscaffold.api.helpers.merge`
- :obj:`~pyscaffold.api.helpers.ensure`
- :obj:`~pyscaffold.api.helpers.reject`

The first function can be used to deep merge a dictionary argument with the
current representation of the to-be-generated directory tree, automatically
considering any metadata present in tuple values. On the other hand, the last
two functions can be used to ensure a single file is present or absent in the
current representation of the project structure, automatically handling parent
directories.

.. note::

    Similarly to the actions list helpers, these functions also **DO NOT**
    modify the project structure. Instead they return a new structure with the
    changhes applied.

The following example illustrates the implementation of a
``define_awesome_files`` action:

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
    from {namespace_pkg}.awesome import awesome

    def test_awesome():
        assert awesome() == "Awesome!"
    """

    def extend_scaffold(actions, helpers):

        # ...

        def define_awesome_files(structure, opts):
            structure = helpers.merge(structure, {
                opts['project']: {
                    opts['package']: {
                        'awesome.py': MY_AWESOME_FILE.format(opts)
                    },
                    'tests': {
                        'awesome_test.py': (
                            MY_AWESOME_TEST.format(opts),
                            helpers.NO_OVERWRITE
                        )
                    }
                }
            })

            structure['.python-version'] = ('3.6.1', helpers.NO_OVERWRITE)

            for filename in opts['awesome_files']:
                structure = helpers.ensure(
                    structure, [opts['project'], 'awesome', filename],
                    content='AWESOME!', update_rule=helpers.NO_CREATE)
                    # The second argument is the file path, represented by a
                    # list of file parts or a string.
                    # Alternatively in this example:
                    # path = '{project}/awesome/{filename}'.format(
                    #           filename=filename, **opts)

            # The `reject` can be used to avoid default files being generated.
            structure = helpers.reject(
                structure, '{project}/{package}/skeleton.py'.format(**opts))
                # Alternatively in this example:
                # path = [opts['project'], opts['package'], 'skeleton.py'])

            # It is import to remember the return values
            return (structure, opts)

        # ...

.. note::

    The ``project`` and  ``package`` options should be used to provide
    the correct location of the files relative to the current working
    directory.

As shown by the previous example, the :mod:`~pyscaffold.api.helpers` argument
also presents constants that can be used as metadata. The ``NO_OVERWRITE`` flag
avoids an existing file to be overwritten when ``putup`` is used in update
mode.  Similarly, ``NO_CREATE`` avoids creating a file from template in update
mode, even if it does not exist.

.. note::

    In order to make use of the ``helpers`` argument, the action needs to be
    declared inside the function responsible for registering it. A different
    approach would be using :obj:`functools.partial` to bind this argument to
    an external function::

        from functools import partial, wraps

        def extend_scaffold(actions, helpers):
            # ...
            add_files = partial(define_awesome_files, helpers)
            add_files = wraps(define_awesome_files)(add_files)
            actions = helpers.register(actions, add_files)
            # ...

        def define_awesome_files(helpers, structure, opts):
            # ...

    When using this approach, it is necessary to adjust the ``__name__`` and
    ``__module__`` properties of the action to ensure the action identifier is
    properly calculated. The function :obj:`functools.wraps` can do that.
    Since this pattern is so common, there is a helper that encapsulates both
    :obj:`functools.partial` and :obj:`functools.wraps`:
    :obj:`~pyscaffold.api.helpers.partial`::

        def extend_scaffold(actions, helpers):
            # ...
            actions = helpers.register(
                actions,
                helpers.partial(define_awesome_files, helpers)
            )
            # ...

        def define_awesome_files(helpers, structure, opts):
            # ...

    In addition, the helper :obj:`~pyscaffold.api.helpers.rpartial` acts
    in a similar way, but binds the given arguments as the last arguments of
    the original function (``rpartial`` stands for **right partial**)::

        def extend_scaffold(actions, helpers):
            # ...
            actions = helpers.register(
                actions,
                helpers.rpartial(define_awesome_files, helpers)
            )
            # ...

        def define_awesome_files(structure, opts, helpers):
            # ...


Activating Extensions
---------------------

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
                            const=extend_scaffold,
                            help='generate awesome extra files')

In this case, an option with the ``append_const`` action is created,
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
            extensions.append(extend_scaffold)
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


Conventions for Community Extensions
====================================

In order to make it easy to find PyScaffold extensions, community packages
should be namespaced as in ``pyscaffoldext.${EXTENSION}`` (where ``${EXTENSION}``
is the name of the extension being developed). Although this naming convention
slightly differs from `PEP423
<https://www.python.org/dev/peps/pep-0423/#use-standard-pattern-for-community-contributions>`_,
it is close enough and shorter.

Similarly to ``sphinxcontrib-*`` packages, names registered in PyPI should
contain a dash ``-``, instead of a dot ``.``. This way, third-party extension
development can be easily bootstrapped with the command::

    putput pyscaffoldext-${EXTENSION} -p ${EXTENSION} --with-namespace pyscaffoldext


Final Considerations
====================

When writing extensions, it is important to be consistent with the default
PyScaffold behavior. In particular, PyScaffold uses a ``pretend`` option to
indicate when the actions should not run but instead just indicate the
expected results to the user, that **MUST** be respected.

The ``pretend`` option is automatically observed for files registered in
the project structure representation, but complex actions may require
specialized coding. The :mod:`~pyscaffold.api.helpers` argument provides a
special :class:`logger <pyscaffold.log.ReportLogger>` object useful in
these situations. Please refer to :ref:`cookiecutter-extension` for a
practical example.

Other options that should be considered are the ``update`` and ``force``
flags. See :obj:`pyscaffold.api.create_project` for a list of available
options.
