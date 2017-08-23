# -*- coding: utf-8 -*-
"""
Custom logging infrastructure to provide execution information for the user.
"""
from __future__ import absolute_import

from contextlib import contextmanager
from logging import INFO, Formatter, LoggerAdapter, StreamHandler, getLogger

DEFAULT_LOGGER = __name__


class ReportFormatter(Formatter):
    """Formatter ."""

    ACTIVITY_MAXLEN = 12
    SPACING = '  '

    def format(self, record):
        """Compose message when a record with report information is given."""
        if hasattr(record, 'activity'):
            activity = self._format_activity(record.activity)
            spacing = self.SPACING * max(record.nesting + 1, 0)
            subject = record.subject
            record.msg = activity + spacing + subject

        return super(ReportFormatter, self).format(record)

    def _format_activity(self, activity):
        actual = len(activity)
        padding = ' ' * max(self.ACTIVITY_MAXLEN - actual, 0)

        return padding + activity


class ReportLogger(LoggerAdapter):
    """Suitable wrapper for PyScaffold CLI interactive execution reports.

    Attributes:
        wrapped (logging.Logger): underlying logger object.
        default_handler (logging.StreamHandler): stream handler configured for
            providing user feedback in PyScaffold CLI.
        nesting (int): current nesting level of the report.
    """

    def __init__(self, logger=None, extra=None):
        self.nesting = 0
        self.wrapped = logger or getLogger(DEFAULT_LOGGER)
        self.extra = extra or {}
        self.default_handler = StreamHandler()
        self.default_handler.setFormatter(ReportFormatter())
        self.wrapped.addHandler(self.default_handler)
        super(ReportLogger, self).__init__(self.wrapped, self.extra)

    def report(self, activity, subject, nesting=None, level=INFO):
        """Log an activity has occurred during scaffold.

        Args:
            activity (str): usually a verb or command, e.g. ``create``,
                ``invoke``, ``run``, ``chdir``...
            subject (str): usually a path in the file system or an action
                identifier.
            nesting (int): optional nesting level. By default it is calculated
                from the activity name.
            level (int): log level. Defaults to :obj:`logging.INFO`.
                See :mod:`logging` for more information.
        """
        return self.wrapped.log(level, '', extra={
            'activity': activity,
            'subject': subject,
            'nesting': nesting or self.nesting
        })

    @contextmanager
    def indent(self, count=1):
        """Temporarily adjust padding while executing a context.

        Example:

            .. code-block:: python

                from pyscaffold.log import logger
                logger.report('invoke', 'custom_action')
                with logger.indent():
                   logger.report('create', 'some/file/path')

                # Expected logs:
                # --------------------------------------
                #       invoke  custom_action
                #       create    some/file/path
                # --------------------------------------
                # Note how the spacing between activity and subject in the
                # second entry is greater than the equivalent in the first one.
        """
        prev = self.nesting
        self.nesting += count
        yield
        self.nesting = prev

    def copy(self):
        """Produce a copy of the wrapped logger.

        Sometimes, it is better to make a copy of th report logger to keep
        indentation consistent.
        """
        clone = self.__class__(self.wrapped, self.extra)
        clone.nesting = self.nesting

        return clone


logger = ReportLogger()
"""Default logger configured for PyScaffold."""
