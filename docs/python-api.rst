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

    import logging

    from pyscaffold.api import create_project
    from pyscaffold.extenstions import tox, travis, namespace
    from pyscaffold.log import DEFAULT_LOGGER as LOGGER_NAME

    logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)

    create_project(project="my-proj-name", author="Your Name",
                   namespace="some.namespace", license="mit",
                   extensions=[tox.extend_project,
                               travis.extend_project,
                               namespace.extend_project])

Note that no built-in extension (e.g. tox, travis and namespace support) is
activated by default.  The ``extensions`` option should be manually populated
when convenient.

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
