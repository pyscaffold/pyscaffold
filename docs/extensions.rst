.. _extensions:

====================
Extending PyScaffold
====================

PyScaffold is carefully designed to cover the essentials of authoring and
distributing Python packages. Most of time, tweaking ``putup`` options is
enough to ensure proper configuration of a project.
However, for advanced use cases PyScaffold can be extended at runtime by other
Python packages, providing a deeper level of programmability and customization.

From the standpoint of PyScaffold, an extension is just an class inheriting
from :obj:`~pyscaffold.extensions.Extension` overriding and implementing
certain methods that allow the manipulation of a *in-memory* **project structure
representation** via PyScaffold's internal **action pipeline** mechanism.
The following sections describe these two key concepts in detail and present a
comprehensive guide about how to create custom extensions.

.. tip::

    A perfect start for your own custom extension is the extension `custom_extension`_
    for PyScaffold. Just install it with ``pip install pyscaffoldext-custom-extension``
    and then create your own extension template with
    ``putup --custom-extension pyscaffoldext-my-own-extension``.


.. include:: project-structure.rst
.. include:: action-pipeline.rst

Creating an Extension
=====================

In order to create an extension it is necessary to write a class that inherits
from :obj:`~pyscaffold.extensions.Extension` and implements the method
:obj:`~pyscaffold.extensions.Extension.activate` that receives a list of
actions (interpret this argument as a sequence of actions to be executed, or
pipeline), registers a custom action that will be called later and returns a
modified version of the list of actions:

.. code-block:: python

    from pyscaffold import actions
    from pyscaffold.extensions import Extension


    class MyExtension(Extension):
        """Help text on commandline when running putup -h"""

        def activate(self, pipeline):
            """Activate extension

            Args:
                pipeline (list): list of actions to perform

            Returns:
                list: updated list of actions
            """
            pipeline = actions.register(pipeline, self.action, after="create_structure")
            pipeline = actions.unregister(pipeline, "init_git")
            return actions

        def action(self, struct, opts):
            """Perform some actions that modifies the structure and options

            Args:
                struct (dict): project representation as (possibly) nested
                    :obj:`dict`.
                opts (dict): given options, see :obj:`create_project` for
                    an extensive list.

            Returns:
                new_struct, new_opts: updated project representation and options
            """
            ...
            return new_struct, new_opts


.. tip::

    The ``register`` and ``unregister`` methods implemented in the module
    :mod:`pyscaffold.actions` basically create modified copies of the
    action list by inserting/removing the specified functions, with some
    awareness about their execution order.


Action List Helper Methods
--------------------------

As implied by the previous example, the :mod:`pyscaffold.actions` module
provides a series of useful functions and makes it easier to manipulate the
action list, by using :obj:`~pyscaffold.actions.register` and
:obj:`~pyscaffold.actions.unregister`.

Since the action order is relevant, the first function accepts special keyword
arguments (``before`` and ``after``) that should be used to place the extension
actions precisely among the default actions. The value of these arguments can
be presented in 2 different forms::

    actions.register(action_sequence, hook1, before="define_structure")
    actions.register(action_sequence, hook2, after="pyscaffold.structure:create_structure")

The first form uses as a position reference the first action with a matching
name, regardless of the module. Accordingly, the second form tries to find an
action that matches both the given name and module. When no reference is given,
:obj:`~pyscaffold.actions.register` assumes as default position
``after="pyscaffold.structure:define_structure"``.  This position is special
since most extensions are expected to create additional files inside the
project. Therefore, it is possible to easily amend the project structure before
it is materialized by ``create_structure``.

The :obj:`~pyscaffold.actions.unregister` function accepts as second
argument a position reference which can similarly present the module name::

        actions.unregister(action_sequence, "init_git")
        actions.unregister(action_sequence, "pyscaffold.api:init_git")

.. note::

    These functions **DO NOT** modify the actions list, instead they return a
    new list with the changes applied.

.. tip::

    For convenience, the functions :obj:`~pyscaffold.actions.register` and
    :obj:`~pyscaffold.actions.unregister` are aliased as instance methods
    of the :obj:`~pyscaffold.extensions.Extension` class.

    Therefore, inside the :obj:`~pyscaffold.extensions.Extension.activate` method, one
    could simply call ``action_sequence = self.register(action_sequence, self.my_action)``.


Structure Helper Methods
------------------------

PyScaffold also provides extra facilities to manipulate the project structure.
The following functions are accessible through the
:mod:`~pyscaffold.structure` module:

- :obj:`~pyscaffold.structure.merge`
- :obj:`~pyscaffold.structure.ensure`
- :obj:`~pyscaffold.structure.reject`
- :obj:`~pyscaffold.structure.modify`

The first function can be used to deep merge a dictionary argument with the
current representation of the to-be-generated directory tree, automatically
considering any file op present in tuple values. On the other hand, the second
and third functions can be used to ensure a single file is present or absent in
the current representation of the project structure, automatically handling
parent directories.  Finally, :obj:`~pyscaffold.structure.modify` can be used
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

    from pyscaffold import structure
    from pyscaffold.extensions import Extension
    from pyscaffold.operations import create, no_overwrite, skip_on_update


    def my_awesome_file(opts):
        return dedent(
            """\
            __author__ = "{author}"
            __copyright__ = "{author}"
            __license__ = "{license}"

            def awesome():
                return "Awesome!"
            """.format(
                **opts
            )
        )


    MY_AWESOME_TEST = Template(
        """\
    import pytest
    from ${qual_pkg}.awesome import awesome

    def test_awesome():
        assert awesome() == "Awesome!"
    """
    )


    class AwesomeFiles(Extension):
        """Adding some additional awesome files"""

        def activate(self, actions):
            return self.register(actions, self.define_awesome_files)

        def define_awesome_files(self, struct, opts):
            struct = structure.merge(
                struct,
                {
                    "src": {
                        opts["package"]: {"awesome.py": my_awesome_file},
                    },
                    "tests": {
                        "awesome_test.py": (MY_AWESOME_TEST, no_overwrite(create)),
                        "other_test.py": ("# not so awesome", no_overwrite(create)),
                    },
                },
            )

            struct[".python-version"] = ("3.6.1", no_overwrite(create))

            for filename in ["awesome_file1", "awesome_file2"]:
                struct = structure.ensure(
                    struct,
                    f"src/{opts['package']}/{filename}",
                    content="AWESOME!",
                    file_op=skip_on_update(create),
                    # The second argument is the file path, represented by a
                    # os.PathLike object or string.
                    # Alternatively in this example:
                    # Path("src", opts["package"], filename),
                )

            # The `reject` can be used to avoid default files being generated.
            struct = structure.reject(struct, Path("src", opts["package"], "skeleton.py"))

            # `modify` can be used to change contents in an existing file
            # and/or change the assigned file operation
            def append_pdb(prev_content, prev_op):
                retrun(prev_content + "\nimport pdb", skip_on_update(prev_op)),

            struct = structure.modify(struct, "tests/other_test.py", append_pdb)

            # It is import to remember the return values
            return struct, opts


As shown by the previous example, the :mod:`~pyscaffold.operations` module
also contains file operation **modifiers** that can be used to change the
assigned file op. These modifiers work like standard `Python decorators`_:
instead of being a file op themselves, they receive a file operation as
argument and return a file operation, and therefore can be used to *wrap* the
original file operation and modify its behaviour.

.. tip::

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

.. tip::

    In order to guarantee consistency and allow PyScaffold to unequivocally find
    your extension, the name of the entry point should be a "underscore" version
    of the name of the extension class (e.g. an entry point ``awesome_files``
    for the ``AwesomeFiles`` class). If you really need to customize that
    behaviour, please overwrite the ``name`` property of your class to match
    the entry point.

By inheriting from :obj:`pyscaffold.extensions.Extension`, a default CLI option that
already activates the extension will be created, based on the dasherized
version of the name in the `setuptools entry point`_. In the example
above, the automatically generated option will be ``--awesome-files``.

For more sophisticated extensions which need to read and parse their
own command line arguments it is necessary to override
:obj:`~pyscaffold.extensions.Extension.augment_cli` that receives an
:class:`argparse.ArgumentParser` argument. This object can then be modified
in order to add custom command line arguments that will later be stored in the
``opts`` dictionary.
Just remember the convention that after the command line arguments parsing,
the extension function should be stored under the ``extensions`` attribute
(a list) of the :mod:`argparse` generated object. For reference check out the
implementation of the :ref:`namespace extension <namespace-extension>`.
Another convention is to avoid storing state/parameters inside the
extension class, instead store them as you would do regularly with
:mod:`argparse` (inside the :obj:`argparse.Namespace` object).


Persisting Extensions for Future Updates
----------------------------------------

PyScaffold will save the name of your extension in a **pyscaffold** section
inside the ``setup.cfg`` files and automatically activate it again every time
the user runs ``putup --update``. To prevent it from happening you can
set ``persist = False`` in your extension instances or class.

PyScaffold can also save extension-specific options if the names of those
options start with an "underscore" version of your extension's name (and
`setuptools entry point`_).
For example, the :ref:`namespace extension <namespace-extension>`
stores the ``namespace`` option in ``setup.cfg``.

If the name of your extension class is ``AwesomeFiles``, then anything like
``opts["awesome_files"]``, ``opts["awesome_files1"]``,
``opts["awesome_files_SOMETHING"]`` would be stored.
Please ensure you have in mind the limitations of the :mod:`configparser`
serialisation mechanism and supported data types to avoid errors (it should be
safe to use string values without line breaks).


Extra Configurations
--------------------

Similarly to ``persist = False``, existing extensions might accept some sort
of metadata to be defined by new extensions.

This is the case of the :mod:`pyscaffold.extensions.interactive`, that allows
users to interactively choose PyScaffold's parameters by editing a file
containing available options alongside a short description (similarly to
``git rebase -i``).
The :mod:`~pyscaffold.extensions.interactive` extension accepts a
``interactive`` attribute defined by extension instances or classes.
This attribute might define a dictionary with keys: ``"ignore"`` and
``"comment"``.
The value associated with the key ``"ignore"`` should be a list of CLI options
to be simply ignored when creating examples (e.g. ``["--help"]``).
The value associated with the key ``"comment"`` should be a list of CLI options
to be commented in the created examples, even if they appear in the
original ``sys.argv``.

.. warning::
   The :obj:`~pyscaffold.extensions.interactive` extension is still
   **experimental** and might not work exactly as expected. More importatly,
   due to limitations on the way :obj:`argparse` is implemented, there are
   several limitations and complexities on how to manipulate command line
   options when not using them directly.
   This means that the interactive extension might render your extension's
   options in a sub-optimal way. If you ever encounter this challenge we
   strongly encourage you to open a `pull request`_ (or at least an issue_ or
   discussion_).

If your extension accepts metadata and interact with other extensions, you can
also rely in informative attributes, but please be sure to make these optional
with good fallback values and a comprehensive documentation.


Examples
========

Some options for the ``putup`` command are already implemented as extensions
and can be used as reference implementation, such as:

* :doc:`no-skeleton </examples/no-skeleton-extension>`
* :doc:`no-tox </examples/no-tox-extension>`
* :doc:`cirrus </examples/cirrus-extension>`
* :doc:`gitlab </examples/gitlab-ci-extension>`

For more advanced extensions, please check:

* :doc:`namespace </examples/namespace-extension>`
* :doc:`pre-commit </examples/pre-commit-extension>`


Public API
==========

The following methods, functions and constants are considered to be part of the public API
of PyScaffold for creating extensions and will not change signature and
described overall behaviour (although implementation details might change) in a
backwards incompatible way between major releases (`semantic versioning`_):

- :obj:`pyscaffold.actions.register`
- :obj:`pyscaffold.actions.unregister`
- :obj:`pyscaffold.extensions.Extension.__init__`
- :obj:`pyscaffold.extensions.Extension.persist`
- :obj:`pyscaffold.extensions.Extension.name`
- :obj:`pyscaffold.extensions.Extension.augment_cli`
- :obj:`pyscaffold.extensions.Extension.activate`
- :obj:`pyscaffold.extensions.Extension.register`
- :obj:`pyscaffold.extensions.Extension.unregister`
- :obj:`pyscaffold.extensions.include`
- :obj:`pyscaffold.extensions.store_with`
- :obj:`pyscaffold.operations.create`
- :obj:`pyscaffold.operations.no_overwrite`
- :obj:`pyscaffold.operations.skip_on_update`
- :obj:`pyscaffold.structure.ensure`
- :obj:`pyscaffold.structure.merge`
- :obj:`pyscaffold.structure.modify`
- :obj:`pyscaffold.structure.reject`
- :obj:`pyscaffold.templates.get_template`

In addition to these, the definition of action (given by
:obj:`pyscaffold.actions.Action`), project structure (given by
:obj:`pyscaffold.structure.Structure`), and operation (given by
:obj:`pyscaffold.operation.FileOp`) are also part of the public API.
The remaining functions and methods are no guaranteed to be stable and are
subject to incompatible changes even in minor/patch releases.


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

.. tip::

    If you want to write a PyScaffold extension, check out our
    `custom_extension`_ generator. It can get you pretty far in just a few
    minutes.


Final Considerations
====================

#. When writing extensions, it is important to be consistent with the default
   PyScaffold behavior. In particular, PyScaffold uses a ``pretend`` option to
   indicate when the actions should not run but instead just indicate the
   expected results to the user, that **MUST** be respected.

   The ``pretend`` option is automatically observed for files registered in
   the project structure representation, but complex actions may require
   specialized coding. The :mod:`~pyscaffold.log` module provides a
   special :class:`logger <pyscaffold.log.ReportLogger>` object useful in
   these situations. Please refer to `pyscaffoldext-cookiecutter`_ for a
   practical example.

   Other options that should be considered are the ``update`` and ``force``
   flags. See :obj:`pyscaffold.api.create_project` for a list of available
   options.

#. Don't forget that packages can be created inside namespaces.
   To be on the safe side when writing templates prefer `explicit relative
   import statements`_ (e.g. ``from . import module``) or use the template
   variable ``${qual_pkg}`` provided by PyScaffold. This variable contains the
   fully qualified package name, including possible namespaces.

   .. code-block:: mako

       # Yes:
       import ${qual_pkg}
       from . import module
       from .module import function
       from ${qual_pkg} import module
       from ${qual_pkg}.module import function

       # No:
       import ${package}
       from ${package} import module
       from ${package}.module import function


.. _PEP423: https://www.python.org/dev/peps/pep-0423/#use-standard-pattern-for-community-contributions
.. _setuptools entry point: https://setuptools.pypa.io/en/stable/userguide/entry_point.html
.. _custom_extension: https://github.com/pyscaffold/pyscaffoldext-custom-extension
.. _Cookiecutter templates: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _Python decorators: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
.. _semantic versioning: https://semver.org
.. _pull request: https://github.com/pyscaffold/pyscaffold/pulls
.. _issue: https://github.com/pyscaffold/pyscaffold/issues
.. _discussion: https://github.com/pyscaffold/pyscaffold/discussions
.. _explicit relative import statements: https://pep8.org/#imports
