# -*- coding: utf-8 -*-
"""
Custom logging infrastructure to provide execution information for the user.
"""
from __future__ import absolute_import, print_function

from contextlib import contextmanager
from logging import INFO, Formatter, LoggerAdapter, StreamHandler, getLogger
from os.path import realpath, relpath

DEFAULT_LOGGER = __name__


def _are_equal_paths(path1, path2):
    return realpath(path1) == realpath(path2)


def _is_current_path(path):
    return _are_equal_paths(path, '.')


class ReportFormatter(Formatter):
    """Formatter ."""

    ACTIVITY_MAXLEN = 12
    SPACING = '  '

    def format(self, record):
        """Compose message when a record with report information is given."""
        if hasattr(record, 'activity'):
            return self.format_report(record)

        return self.format_default(record)

    def create_padding(self, activity):
        """Create the appropriate padding in order to align activities."""
        actual = len(activity)
        count = max(self.ACTIVITY_MAXLEN - actual, 0)
        return ' ' * count

    def format_path(self, path):
        """Simplify paths to avoid wasting space in terminal."""

        if path[0] in './~':
            # Heuristic to determine if subject is a file path
            # that needs to be made short
            abbrev = relpath(path)

            if len(abbrev) < len(path):
                # Ignore if not shorter
                path = abbrev

        return path

    def format_activity(self, activity):
        """Format the activity keyword."""
        return activity

    def format_subject(self, subject):
        """Format the subject of the activity."""
        return self.format_path(subject)

    def format_target(self, target):
        """Format extra information about the activity target."""
        if target and not _is_current_path(target):
            return 'to ' + repr(self.format_path(target))

        return ''

    def format_context(self, context):
        """Format extra information about the activity context."""
        if context and not _is_current_path(context):
            return 'from ' + repr(self.format_path(context))

        return ''

    def format_default(self, record):
        """Format default log messages."""
        return super(ReportFormatter, self).format(record)

    def format_report(self, record):
        """Compose message when a custom record is given."""
        record.msg = (
            self.create_padding(record.activity) +
            self.format_activity(record.activity) +
            self.SPACING * max(record.nesting + 1, 0) +
            ' '.join([
                text for text in [
                    self.format_subject(record.subject),
                    self.format_target(record.target),
                    self.format_context(record.context)
                ] if text  # Filter empty strings
            ])
        )

        return super(ReportFormatter, self).format(record)


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

    def report(self, activity, subject,
               context=None, target=None, nesting=None, level=INFO):
        """Log that an activity has occurred during scaffold.

        Args:
            activity (str): usually a verb or command, e.g. ``create``,
                ``invoke``, ``run``, ``chdir``...
            subject (str): usually a path in the file system or an action
                identifier.
            context (str): path where the activity take place.
            target (str): path affected by the activity
            nesting (int): optional nesting level. By default it is calculated
                from the activity name.
            level (int): log level. Defaults to :obj:`logging.INFO`.
                See :mod:`logging` for more information.

        Notes:
            This method creates a custom log record, with additional fields:
            **activity**, **subject**, **context**, **target** and **nesting**,
            but an empty **msg** field. The :class:`ReportFormatter`
            creates the log message from the other fields.

            Often **target** and **context** complement the logs when
            **subject** does not hold all the necessary information. For
            example::

                logger.report('copy', 'my/file', target='my/awesome/path')
                logger.report('run', 'command', context='current/working/dir')
        """
        return self.wrapped.log(level, '', extra={
            'activity': activity,
            'subject': subject,
            'context': context,
            'target': target,
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
        try:
            prev = self.nesting
            self.nesting += count
            yield
        finally:
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
