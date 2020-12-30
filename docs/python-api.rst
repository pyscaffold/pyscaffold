.. _python-api:

====================
Embedding PyScaffold
====================

PyScaffold is expected to be used from terminal, via ``putup`` command line
application. It is, however, possible to write an external script or program
that embeds PyScaffold and use it to perform some custom actions.

The public Python API for embedding PyScaffold is composed by the main function
:obj:`pyscaffold.api.create_project` in addition to :obj:`pyscaffold.api.NO_CONFIG`,
:obj:`pyscaffold.log.DEFAULT_LOGGER`, :obj:`pyscaffold.log.logger` (partially,
see details bellow), and the constructors for the extension classes belonging
to the :mod:`pyscaffold.extenstions` module (the other methods and functions
are not considered part of the API). This API, as explicitly listed, follows
`semantic versioning`_ and will not change in a backwards incompatible way
between releases. The remaining methods and functions are not guaranteed to be stable.

The following example illustrates a typical embedded usage of PyScaffold:

.. code-block:: python

    import logging

    from pyscaffold.api import create_project
    from pyscaffold.extenstions.cirrus import Cirrus
    from pyscaffold.extenstions.namespace import Namespace
    from pyscaffold.log import DEFAULT_LOGGER as LOGGER_NAME

    logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)

    create_project(
        project_path="my-proj-name",
        author="Your Name",
        namespace="some.namespace",
        license="MIT",
        extensions=[Cirrus(), Namespace()],
    )

Note that no built-in extension (e.g. **cirrus** and **namespace**)
is activated by default. The ``extensions`` option should be manually
populated when convenient.

PyScaffold uses the logging infrastructure from Python standard library, and
emits notifications during its execution. Therefore, it is possible to control
which messages are logged by properly setting the log level (internally, most
of the messages are produced under the ``INFO`` level).  By default, a
:class:`~logging.StreamHandler` is attached to the logger, however it is
possible to replace it with a custom handler using
:obj:`logging.Logger.removeHandler` and :obj:`logging.Logger.addHandler`. The
logger object is available under the :obj:`~pyscaffold.log.logger` variable of
the :mod:`pyscaffold.log` module. The default handler is available under the
:obj:`~pyscaffold.log.ReportLogger.handler` property of the
:obj:`~pyscaffold.log.logger` object.


.. _semantic versioning: https://semver.org
