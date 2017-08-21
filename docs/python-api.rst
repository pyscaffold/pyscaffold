.. _python-api:

====================
Embedding PyScaffold
====================

PyScaffold is expected to be used from terminal, via ``putup`` command line
application. It is, however, possible to write an external script or program
that embeds PyScaffold and use it to perform some custom actions.

The public Python API is exposed by the :mod:`pyscaffold.api` module, which
contains the main function :obj:`~pyscaffold.api.create_project`.
The following example illustrates a typical embedded usage of PyScaffold:

.. code-block:: python

    from pyscaffold.api import create_project
    from pyscaffold.extenstions import tox, travis

    create_project(project="my-proj-name", author="Your Name",
                   namespace="some.namespace", license="mit",
                   extensions=[tox.extend_project, travis.extend_project])

Note that no built-in extension (e.g. tox and travis support) is activated by default.
The ``extensions`` option should be manually populated when convenient
