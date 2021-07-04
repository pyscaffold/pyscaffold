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

.. note::

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

        {"file": ("content", no_overwrite(create))}

    will prevent the ``file`` to be written if it already exists. See
    :mod:`pyscaffold.operations` for more information on how to write your own
    file operation and other options.

Finally, while it is simple to represent file contents as a string directly,
most of the times we want to *customize* them according to the project
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
