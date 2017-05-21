.. _python-api:

====================
Embedding PyScaffold
====================

PyScaffold is expected to be used from terminal, via ``putup`` command line
application. It is, however, possible to write an external script or program
that embeds PyScaffold and use it to perform some custom actions.

The public Python API is exposed by the :mod:`pyscaffold.api` module, which
contains two main functions, :obj:`~pyscaffold.api.get_default_opts` and
:obj:`~pyscaffold.api.create_project`, as well as the
:mod:`~pyscaffold.api.Scaffold` class (required by the specification of the
extension API).

The follow examples illustrates a typical embedded usage of PyScaffold:

.. code-block:: python

    from pyscaffold.api import get_default_opts, create_project
    from pyscaffold.extenstions import tox, travis

    opts = get_default_opts("my-proj-name", author="Your Name",
                            namespace="some.namespace", license="mit",
                            extensions=[tox.extend_project,
                                        travis.extend_project])
    create_project(opts)

Although :obj:`~pyscaffold.api.get_default_opts` is not strictly required,
it is highly recommended to use these two functions together.
It just makes it easier to call :obj:`~pyscaffold.api.create_project` and
skip the boring option passing.

