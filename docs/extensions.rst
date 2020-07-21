.. _extensions:

====================
Extending PyScaffold
====================

PyScaffold is carefully designed to cover the essentials of authoring and
distributing Python packages. Most of time, tweaking ``putup`` options is
enough to ensure proper configuration of a project.
However, for advanced use cases a deeper level of programmability may be
required and PyScaffold's extension systems provides this.

PyScaffold can be extended at runtime by other Python packages.
Therefore it is possible to change the behaviour of the ``putup`` command line
tool without changing the PyScaffold code itself. In order to explain how this
mechanism works, the following sections define a few important concepts and
present a comprehensive guide about how to create custom extensions.

Additionally, `Cookiecutter templates`_ can also be used but writing a native
PyScaffold extension is the preferred way.

.. note::

    A perfect start for your own custom extension is the extension `custom_extension`_
    for PyScaffold. Just install it with ``pip install pyscaffoldext-custom-extension``
    and then create your own extension template with
    ``putup --custom-extension pyscaffoldext-my-own-extension``.

.. _coreconcepts:

Project Structure Representation
================================

Each Python package project is internally represented by PyScaffold as a tree
data structure, that directly relates to a directory entry in the file system.
This tree is implemented as a simple (and possibly nested) :obj:`dict` in which
keys indicate the path where files will be generated, while values indicate
their content. For instance, the following dict::

    {
        "folder": {
            "file.txt": "Hello World!",
            "another-folder": {
                "empty-file.txt": ""
            }
        }
    }

represents a project directory in the file system that contains a single
directory named ``folder``. In turn, ``folder`` contains two entries.
The first entry is a file named ``file.txt`` with content ``Hello World!``
while the second entry is a sub-directory named ``another-folder``. Finally,
``another-folder`` contains an empty file named ``empty-file.txt``.

.. versionchanged:: 4.0
    Prior to version 4.0, the project structure included the top level
    directory of the project. Now it considers everything **under** the
    project folder.

Additionally, tuple values are also allowed in order to specify a
**file operation** (or simply **file op**) that will be used to produce the file.
In this case, the first element of the tuple is the file content, while the
second element will be a function (or more generally a :obj:`callable` object)
responsible for writing that content to the disk. For example, the dict::

    from pyscaffold.operations import create

    {
        "src": {
            "namespace": {
                "module.py": ('print("Hello World!")', create)
            }
        }
    }

represents a ``src/namespace/module.py`` file, under the project directory,
with content ``print("Hello World!")``, that will written to the disk.
When no operation is specified (i.e. when using a simple string instead of a
tuple), PyScaffold will assume :obj:`~pyscaffold.operations.create` by default.

.. note::

    The :obj:`~pyscaffold.operations.create` function simply creates a text file
    to the disk using UTF-8 encoding and the default file permissions. This
    behaviour can be modified by wrapping :obj:`~pyscaffold.operations.create`
    within other fuctions/callables, for example::

        from pyscaffold.operations import create, no_overwrite

        {"file": ("content", no_overwrite(create)}

    will prevent the ``file`` to be written if it already exists. See
    :mod:`pyscaffold.operations` for more information on how to write your own
    file operation and other options.

Finally, while it is simple to represent file contents as a string directly,
most of he times we want to *customize* them according to the project
parameters being created (e.g. package or author's name). So PyScaffold also
accepts :obj:`string.Template` objects and functions (with a single :obj:`dict`
argument and a :obj:`str` return value) to be used as contents. These templates
and functions will be called with :obj:`PyScaffold's options
<pyscaffold.operations.ScaffoldOpts>` when its time to create the file to the
disk.

.. note::

    :obj:`string.Template` objects will have :obj:`~string.Template.safe_substitute`
    called (not simply :obj:`~string.Template.substitute`).

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
        return new_struct, new_opts

The output of each action is used as the input of the subsequent action, and
initially the structure argument is just an empty dict. Each action is uniquely
identified by a string in the format ``<module name>:<function name>``,
similarly to the convention used for a `setuptools entry point`_.
For example, if an action is defined in the ``action`` function of the
``extras.py`` file that is part of the ``pyscaffoldext.contrib`` project,
the **action identifier** is ``pyscaffoldext.contrib.extras:action``.

By default, the sequence of actions taken by PyScaffold is:

#. :obj:`pyscaffold.api:get_default_options <pyscaffold.api.get_default_options>`
#. :obj:`pyscaffold.api:verify_options_consistency <pyscaffold.api.verify_options_consistency>`
#. :obj:`pyscaffold.structure:define_structure <pyscaffold.structure.define_structure>`
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

From the standpoint of PyScaffold, an extension is just an class inheriting
from :obj:`~pyscaffold.api.Extension` overriding and
implementing certain methods. This methods allow inject actions at arbitrary
positions in the aforementioned list. Furthermore, extensions can also remove
actions.

Creating an Extension
=====================

In order to create an extension it is necessary to write a class that inherits
from :obj:`~pyscaffold.api.Extension` and implements the method
:obj:`~pyscaffold.api.Extension.activate` that receives a list of actions,
registers a custom action that will be called later and returns a modified version
of the list of actions:

.. code-block:: python

    from ..api import Extension
    from ..api import helpers


    class MyExtension(Extension):
        """Help text on commandline when running putup -h"""
        def activate(self, actions):
            """Activate extension

            Args:
                actions (list): list of actions to perform

            Returns:
                list: updated list of actions
            """
            actions = helpers.register(actions, self.action, after="create_structure")
            actions = helpers.unregister(actions, "init_git")
            return actions

        def action(self, struct, opts):
            """Perform some actions that modifies the structure and options

            Args:
                struct (dict): project representation as (possibly) nested
                    :obj:`dict`.
                opts (dict): given options, see :obj:`create_project` for
                    an extensive list.

            Returns:
                struct, opts: updated project representation and options
            """
            ...
            return new_actions, new_opts


.. note::

    The ``register`` and ``unregister`` methods implemented in the module
    :mod:`pyscaffold.api.helpers` basically create modified copies of the
    action list by inserting/removing the specified functions, with some
    awareness about their execution order.


Action List Helper Methods
--------------------------

As implied by the previous example, the :mod:`~pyscaffold.api.helpers` module
provides a series of useful functions and makes it easier to manipulate the
action list, by using :obj:`~pyscaffold.api.helpers.register` and
:obj:`~pyscaffold.api.helpers.unregister`.

Since the action order is relevant, the first function accepts special keyword
arguments (``before`` and ``after``) that should be used to place the extension
actions precisely among the default actions.  The value of these arguments can
be presented in 2 different forms::

    helpers.register(actions, hook1, before="define_structure")
    helpers.register(actions, hook2, after="pyscaffold.structure:create_structure")

The first form uses as a position reference the first action with a matching
name, regardless of the module. Accordingly, the second form tries to find an
action that matches both the given name and module. When no reference is given,
:obj:`~pyscaffold.api.helpers.register` assumes as default position
``after="pyscaffold.structure:define_structure"``.  This position is special
since most extensions are expected to create additional files inside the
project. Therefore, it is possible to easily amend the project structure before
it is materialized by ``create_structure``.

The :obj:`~pyscaffold.api.helpers.unregister` function accepts as second
argument a position reference which can similarly present the module name::

        helpers.unregister(actions, "init_git")
        helpers.unregister(actions, "pyscaffold.api:init_git")

.. note::

    These functions **DO NOT** modify the actions list, instead they return a
    new list with the changes applied.

.. note::

    For convenience, the functions :obj:`~pyscaffold.api.helpers.register` and
    :obj:`~pyscaffold.api.helpers.unregister` are aliased as instance methods
    of the :obj:`~pyscaffold.api.Extension` class.

    Therefore, inside the :obj:`~pyscaffold.api.Extension.activate` method, one
    could simply call ``actions = self.register(actions, self.my_action)``.


Structure Helper Methods
------------------------

PyScaffold also provides extra facilities to manipulate the project structure.
The following functions are accessible through the
:mod:`~pyscaffold.api.helpers` module:

- :obj:`~pyscaffold.api.helpers.merge`
- :obj:`~pyscaffold.api.helpers.ensure`
- :obj:`~pyscaffold.api.helpers.reject`
- :obj:`~pyscaffold.api.helpers.modify`

The first function can be used to deep merge a dictionary argument with the
current representation of the to-be-generated directory tree, automatically
considering any file op present in tuple values. On the other hand, the second
and third functions can be used to ensure a single file is present or absent in
the current representation of the project structure, automatically handling
parent directories.  Finally, :obj:`~pyscaffold.api.helpers.modify` can be used
to change the contents of an existing file in the project structure and/or
the assigned file operation (for example wrapping it with
:obj:`~pyscaffold.operations.no_overwrite`, :obj:`~pyscaffold.operations.skip_on_update`
or :obj:`~pyscaffold.operations.add_permissions`).

.. note::

    Similarly to the actions list helpers, these functions also **DO NOT**
    modify the project structure. Instead they return a new structure with the
    changes applied.

The following example illustrates the implementation of a ``AwesomeFiles``
extension which defines the ``define_awesome_files`` action:

.. code-block:: python

    from pathlib import Path
    from string import Template
    from textwrap import dedent

    from pyscaffold.api import Extension
    from pyscaffold.api import helpers
    from pyscaffold.operations import create, no_overwrite, skip_on_update

    def my_awesome_file(opts):
        return dedent(
            """\
            # -*- coding: utf-8 -*-

            __author__ = "{author}"
            __copyright__ = "{author}"
            __license__ = "{license}"

            def awesome():
                return "Awesome!"
            """.format(**opts)
        )

    MY_AWESOME_TEST = Template("""\
    import pytest
    from ${qual_pkg}.awesome import awesome

    def test_awesome():
        assert awesome() == "Awesome!"
    """)

    class AwesomeFiles(Extension):
        """Adding some additional awesome files"""
        def activate(self, actions):
            return helpers.register(actions, self.define_awesome_files)

        def define_awesome_files(self, struct, opts):
            struct = helpers.merge(struct, {
                "src": {
                    opts["package"]: {"awesome.py": my_awesome_file},
                }
                "tests": {
                    "awesome_test.py": (MY_AWESOME_TEST, no_overwrite(create))
                    "other_test.py": ("# not so awesome", no_overwrite(create))
                }
            })

            struct[".python-version"] = ("3.6.1", no_overwrite(create))

            for filename in ["awesome_file1", "awesome_file2"]:
                struct = helpers.ensure(
                    struct,
                    f"src/{opts['package']}/{filename}"
                    content="AWESOME!",
                    file_op=skip_on_update(create),
                    # The second argument is the file path, represented by a
                    # os.PathLike object.
                    # Alternatively in this example:
                    # Path("src", opts["package"], filename),
                )

            # The `reject` can be used to avoid default files being generated.
            struct = helpers.reject(struct, Path("src", opts["package"], "skeleton.py"))

            # `modify` can be used to change contents in an existing file
            # and/or change the assigned file operation
            def append_pdb(prev_content, prev_op):
                retrun (prev_content +  "\nimport pdb", skip_on_update(prev_op)),

            struct = helpers.modify(struct, "tests/other_test.py", append_pdb)

            # It is import to remember the return values
            return struct, opts


.. note::

    The ``package`` option should be used to provide
    the correct location of the files relative to the current working
    directory.

As shown by the previous example, the :mod:`~pyscaffold.operations` module
also contains file operation **modifiers** that can be used to change the
assigned file op. These modifiers work like standard `Python decorators`_:
instead of being a file op themselves, they receive a file operation as
argument and return a file operation, and therefore can be used to *wrap* the
original file operation and modify its behaviour.

.. note::

    By default, all the file op modifiers in the :obj:`pyscaffold.operations`
    package don't even need an explicit argument, when called with zero
    arguments :obj:`~pyscaffold.operations.create` is assumed.

:obj:`~pyscaffold.operations.no_overwrite` avoids an existing file to be
overwritten when ``putup`` is used in update mode.
Similarly, :obj:`~pyscaffold.operations.skip_on_update` avoids creating a
file from template in update mode, even if it does not exist.
On the other hand, :obj:`~pyscaffold.operations.add_permissions` will change
the file access permissions if it is created or already exists in the disk.


.. note::

    See :mod:`pyscaffold.operations` for more information on how to write your
    own file operation or modifiers.


Activating Extensions
---------------------

PyScaffold extensions are not activated by default. Instead, it is necessary
to add a CLI option to do it.
This is possible by setting up a `setuptools entry point`_ under the
``pyscaffold.cli`` group.
This entry point should point to our extension class, e.g. ``AwesomeFiles``
like defined above. If you for instance use a scaffold generated by PyScaffold
to write a PyScaffold extension (we hope you do ;-), you would add the following
to the ``options.entry_points`` section in ``setup.cfg``:

.. code-block:: ini

    [options.entry_points]
    pyscaffold.cli =
        awesome_files = your_package.your_module:AwesomeFiles

By inheriting from :class:`pyscaffold.api.Extension`, a default CLI option that
already activates the extension will be created, based on the dasherized
version of the name in `setuptools entry point`_ you created. In the example
above, the automatically generated option will be ``--awesome-files``.

For more sophisticated extensions which need to read and parse their
own command line arguments it is necessary to override
:obj:`~pyscaffold.api.Extension.augment_cli` that receives an
:class:`argparse.ArgumentParser` argument. This object can then be modified
in order to add custom command line arguments that will later be stored in the
``opts`` dictionary.
Just remember the convention that after the command line arguments parsing,
the extension function should be stored under the ``extensions`` attribute
(a list) of the :mod:`argparse` generated object. For reference check out the
implementation of the :ref:`namespace extension <examples/namespace-extension>`
as well as the `pyproject extension`_ which serves as a blueprint for new
extensions. Another convention is to avoid storing state/parameters inside the
extension class, instead store them as you would do regularly with
:mod:`argparse` (inside the :obj:`argparse.Namespace` object).


Examples
========

Some options for the ``putup`` command are already implemented as extensions
and can be used as reference implementation:

.. toctree::
   :maxdepth: 2

   namespace <examples/namespace-extension>
   no-skeleton <examples/no-skeleton-extension>
   pre-commit <examples/pre-commit-extension>
   tox <examples/tox-extension>
   travis <examples/travis-extension>
   gitlab <examples/gitlab-ci-extension>


Conventions for Community Extensions
====================================

In order to make it easy to find PyScaffold extensions, community packages
should be namespaced as in ``pyscaffoldext.${EXT_NAME}`` (where ``${EXT_NAME}``
is the name of the extension being developed). Although this naming convention
slightly differs from `PEP423`_, it is close enough and shorter.

Similarly to ``sphinxcontrib-*`` packages, names registered in PyPI should
contain a dash ``-``, instead of a dot ``.``. This way, third-party extension
development can be easily bootstrapped with the command::

    putup pyscaffoldext-${EXT_NAME} -p ${EXT_NAME} --namespace pyscaffoldext --no-skeleton

If you put your extension code in the module ``extension.py`` then the
``options.entry_points`` section in ``setup.cfg`` looks like:

.. code-block:: ini

    [options.entry_points]
    pyscaffold.cli =
        awesome_files = pyscaffoldext.${EXT_NAME}.extension:AwesomeFiles

In this example, ``AwesomeFiles`` represents the name of the class that
implements the extension and ``awesome_files`` is the string used to create
the flag for the ``putup`` command (``--awesome-files``).

.. note::

    If you want to write a PyScaffold extension, please consider
    using our `custom_extension`_ generator.


Final Considerations
====================

When writing extensions, it is important to be consistent with the default
PyScaffold behavior. In particular, PyScaffold uses a ``pretend`` option to
indicate when the actions should not run but instead just indicate the
expected results to the user, that **MUST** be respected.

The ``pretend`` option is automatically observed for files registered in
the project structure representation, but complex actions may require
specialized coding. The :mod:`~pyscaffold.api.helpers` module provides a
special :class:`logger <pyscaffold.log.ReportLogger>` object useful in
these situations. Please refer to `pyscaffoldext-cookiecutter`_ for a
practical example.

Other options that should be considered are the ``update`` and ``force``
flags. See :obj:`pyscaffold.api.create_project` for a list of available
options.

.. _PEP423: https://www.python.org/dev/peps/pep-0423/#use-standard-pattern-for-community-contributions
.. _setuptools entry point: http://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=dynamic#dynamic-discovery-of-services-and-plugins
.. _pyproject extension: https://github.com/pyscaffold/pyscaffoldext-pyproject
.. _custom_extension: https://github.com/pyscaffold/pyscaffoldext-custom-extension
.. _Cookiecutter templates: https://github.com/pyscaffoldext-cookiecutter
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffoldext-cookiecutter
.. _Python decorators: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
