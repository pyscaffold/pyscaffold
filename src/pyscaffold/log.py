"""
Custom logging infrastructure to provide execution information for the user.
"""
import logging
from collections import defaultdict
from contextlib import contextmanager
from logging import INFO, Formatter, LoggerAdapter, StreamHandler, getLogger
from os.path import realpath, relpath
from os.path import sep as pathsep
from typing import DefaultDict, Optional, Sequence

from . import termui

DEFAULT_LOGGER = __name__
"""Name of PyScaffold's default logger (it can be used with :obj:`logging.getLogger`)"""

Styles = Sequence[str]


def _are_equal_paths(path1, path2):
    return realpath(str(path1)) == realpath(str(path2))


def _is_current_path(path):
    return _are_equal_paths(path, ".")


class ReportFormatter(Formatter):
    """Formatter that understands custom fields in the log record."""

    ACTIVITY_MAXLEN = 12
    SPACING = "  "
    CONTEXT_PREFIX = "from"
    TARGET_PREFIX = "to"

    def format(self, record):
        """Compose message when a record with report information is given."""
        if hasattr(record, "activity"):
            return self.format_report(record)

        return self.format_default(record)

    def create_padding(self, activity):
        """Create the appropriate padding in order to align activities."""
        actual = len(activity)
        count = max(self.ACTIVITY_MAXLEN - actual, 0)
        return " " * count

    def format_path(self, path):
        """Simplify paths to avoid wasting space in terminal."""
        from .file_system import is_pathname_valid  # late import due to cycles

        # TODO: Rather handle Path objects instead converting to str
        path = str(path)

        if is_pathname_valid(path) and pathsep in path:
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

    # Subclasses may need the activity name to choose correct format,
    # so the following 3 methods accept a second parameter
    # (even if they not use it)
    def format_subject(self, subject, _activity=None):
        """Format the subject of the activity."""
        return self.format_path(subject) if subject else ""

    def format_target(self, target, _activity=None):
        """Format extra information about the activity target."""
        if target and not _is_current_path(target):
            return f"{self.TARGET_PREFIX} '{self.format_path(target)}'"

        return ""

    def format_context(self, context, _activity=None):
        """Format extra information about the activity context."""
        if context and not _is_current_path(context):
            return f"{self.CONTEXT_PREFIX} '{self.format_path(context)}'"

        return ""

    def format_default(self, record):
        """Format default log messages."""
        record.msg = self.SPACING * max(record.nesting, 0) + record.msg

        return super(ReportFormatter, self).format(record)

    def format_report(self, record):
        """Compose message when a custom record is given."""
        activity = record.activity
        record.msg = (
            self.create_padding(activity)
            + self.format_activity(activity)
            + self.SPACING * max(record.nesting + 1, 0)
            + " ".join(
                [
                    text
                    for text in [
                        self.format_subject(record.subject, activity),
                        self.format_target(record.target, activity),
                        self.format_context(record.context, activity),
                    ]
                    if text  # Filter empty strings
                ]
            )
        )

        return super(ReportFormatter, self).format(record)


class ColoredReportFormatter(ReportFormatter):
    """Format logs with ANSI colors."""

    ACTIVITY_STYLES: DefaultDict[str, Styles] = defaultdict(
        lambda: ("blue", "bold"),
        create=("green", "bold"),
        move=("green", "bold"),
        remove=("red", "bold"),
        delete=("red", "bold"),
        skip=("yellow", "bold"),
        run=("magenta", "bold"),
        invoke=("bold",),
    )

    SUBJECT_STYLES: DefaultDict[str, Styles] = defaultdict(tuple, invoke=("blue",))

    LOG_STYLES: DefaultDict[str, Styles] = defaultdict(
        tuple,
        debug=("green",),
        info=("blue",),
        warning=("yellow",),
        error=("red",),
        critical=("red", "bold"),
    )

    CONTEXT_PREFIX = termui.decorate(ReportFormatter.CONTEXT_PREFIX, "magenta", "bold")

    TARGET_PREFIX = termui.decorate(ReportFormatter.TARGET_PREFIX, "magenta", "bold")

    def format_activity(self, activity):
        return termui.decorate(activity, *self.ACTIVITY_STYLES[activity])

    def format_subject(self, subject, activity=None):
        parent = super(ColoredReportFormatter, self)
        subject = parent.format_subject(subject, activity)
        return termui.decorate(subject, *self.SUBJECT_STYLES[activity])

    def format_default(self, record):
        record.msg = termui.decorate(
            record.msg, *self.LOG_STYLES[record.levelname.lower()]
        )
        return super(ColoredReportFormatter, self).format_default(record)


class ReportLogger(LoggerAdapter):
    """Suitable wrapper for PyScaffold CLI interactive execution reports.

    Args:
        logger (logging.Logger): custom logger to be used. Optional: the
            default logger will be used.
        handlers (logging.Handler): custom logging handler to be used.
            Optional: a :class:`logging.StreamHandler` is used by default.
        formatter (logging.Formatter): custom formatter to be used.
            Optional: by default a :class:`~.ReportFormatter` is created and
            used.
        extra (dict): extra attributes to be merged into the log record.
            Options, empty by default.
        propagate (bool): whether or not to propagate messages in the logging hierarchy,
            ``False`` by default. See :obj:`logging.Logger.propagate`.

    Attributes:
        nesting (int): current nesting level of the report.
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        handler: Optional[logging.Handler] = None,
        formatter: Optional[logging.Formatter] = None,
        extra: Optional[dict] = None,
        propagate=False,
    ):
        self.nesting = 0
        self._wrapped: logging.Logger = logger or getLogger(DEFAULT_LOGGER)
        self.propagate = propagate
        self.extra = extra or {}
        self.handler = handler or StreamHandler()
        self.formatter = formatter or ReportFormatter()
        super(ReportLogger, self).__init__(self._wrapped, self.extra)

    @property
    def propagate(self) -> bool:
        """Whether or not to propagate messages in the logging hierarchy,
        See :obj:`logging.Logger.propagate`.
        """
        return self._propagate

    @propagate.setter
    def propagate(self, value: bool):
        self._propagate = value
        self._wrapped.propagate = value

    @property
    def wrapped(self) -> logging.Logger:
        """Underlying logger object"""
        return self._wrapped

    @wrapped.setter
    def wrapped(self, value: logging.Logger):
        self._wrapped = value
        value.propagate = self.propagate
        self.handler = getattr(self, "_handler", None)

    @property
    def handler(self) -> logging.Handler:
        """Stream handler configured for providing user feedback in PyScaffold CLI"""
        return self._handler

    @handler.setter
    def handler(self, value: logging.Handler):
        self._handler = value
        self._wrapped.handlers.clear()
        self._wrapped.addHandler(self._handler)

    @property
    def formatter(self) -> logging.Formatter:
        """Formatter configured in the default handler"""
        return self._formatter

    @formatter.setter
    def formatter(self, value: logging.Formatter):
        self._formatter = value
        self.handler.setFormatter(value)

    @property
    def level(self):
        """Effective level of the logger"""
        return self.wrapped.getEffectiveLevel()

    @level.setter
    def level(self, value):
        """Set the logger level"""
        self.wrapped.setLevel(value)

    def process(self, msg, kwargs):
        """Method overridden to augment LogRecord with the `nesting` attribute"""
        (msg, kwargs) = super(ReportLogger, self).process(msg, kwargs)
        extra = kwargs.get("extra", {})
        extra["nesting"] = self.nesting
        kwargs["extra"] = extra
        return msg, kwargs

    def report(
        self, activity, subject, context=None, target=None, nesting=None, level=INFO
    ):
        """Log that an activity has occurred during scaffold.

        Args:
            activity (str): usually a verb or command, e.g. ``create``,
                ``invoke``, ``run``, ``chdir``...
            subject (str or os.PathLike): usually a path in the file system or
                an action identifier.
            context (str or os.PathLike): path where the activity take place.
            target (str or os.PathLike): path affected by the activity
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
        return self.wrapped.log(
            level,
            "",
            extra={
                "activity": activity,
                "subject": subject,
                "context": context,
                "target": target,
                "nesting": nesting or self.nesting,
            },
        )

    @contextmanager
    def indent(self, count=1):
        """Temporarily adjust padding while executing a context.

        Example:

            .. code-block:: python

                from pyscaffold.log import logger

                logger.report("invoke", "custom_action")
                with logger.indent():
                    logger.report("create", "some/file/path")

                # Expected logs:
                # --------------------------------------
                #       invoke  custom_action
                #       create    some/file/path
                # --------------------------------------
                # Note how the spacing between activity and subject in the
                # second entry is greater than the equivalent in the first one.

        Note:
            This method is not thread-safe and should be used with care.
        """
        prev = self.nesting
        self.nesting += count
        try:
            yield
        finally:
            self.nesting = prev

    def copy(self):
        """Produce a copy of the wrapped logger.

        Sometimes, it is better to make a copy of th report logger to keep
        indentation consistent.
        """
        clone = self.__class__(
            self.wrapped, self.handler, self.formatter, self.extra, self.propagate
        )
        clone.nesting = self.nesting

        return clone

    def reconfigure(self, opts: Optional[dict] = None, **kwargs):
        """Reconfigure some aspects of the logger object.

        Args:
            opts (dict): dict with the same elements as the keyword arguments bellow

        Keyword Args:
            log_level: One of the log levels specified in the :obj:`logging` module.
            use_colors: automatically set a colored formatter to the logger
                if ANSI codes support is detected. (Defaults to `True`).

        Additional keyword arguments will be ignored.
        """
        opts = (opts or {}).copy()
        opts.update(kwargs)

        if "log_level" in opts:
            self.level = opts["log_level"]

        # if terminal supports, use colors
        stream = getattr(self.handler, "stream", None)
        if opts.get("use_colors", True) and termui.supports_color(stream):
            self.formatter = ColoredReportFormatter()
            self.handler.setFormatter(self.formatter)

        return self


logger = ReportLogger()
"""Default logger configured for PyScaffold."""
