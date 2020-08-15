import logging
import re
from os import getcwd
from os.path import abspath

import pytest

from pyscaffold.file_system import localize_path as lp
from pyscaffold.log import (
    DEFAULT_LOGGER,
    ColoredReportFormatter,
    ReportFormatter,
    ReportLogger,
    logger,
)

from .helpers import uniqstr
from .log_helpers import (
    ansi_pattern,
    ansi_regex,
    make_record,
    match_record,
    match_report,
)

# When adding tests to this file, please have in mind that the global shared
# logging strategy followed by Python and PyScaffold can lead to pain while
# testing. Try to create a new ReportLogger with a brand new underlying native
# Logger object as much as possible (see test_pass_handler for an example), and
# just deactivate the `isolated_logger` fixture with the `original_logger` mark
# if really necessary.


@pytest.fixture
def uniq_raw_logger():
    return logging.getLogger(uniqstr())


# -- Handler Registration --


@pytest.mark.original_logger  # Avoid autouse fixture
def test_default_handler_registered():
    # When the module is imported,
    # Then a default handler should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    assert raw_logger.handlers
    assert isinstance(raw_logger.handlers[0], logging.StreamHandler)
    assert isinstance(raw_logger.handlers[0].formatter, ReportFormatter)


def test_pass_handler(uniq_raw_logger):
    # When the report logger is created with a handler
    handler = logging.NullHandler()
    new_logger = ReportLogger(uniq_raw_logger, handler=handler)
    assert isinstance(new_logger.handler, logging.NullHandler)


# -- Formatter Registration --


@pytest.mark.original_logger
def test_default_formatter_registered():
    # When the module is imported,
    # Then a default formatter should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    handler = raw_logger.handlers[0]
    assert isinstance(handler.formatter, ReportFormatter)


def test_pass_formatter(uniq_raw_logger):
    # When the report logger is created with a formatter
    # Then that formatter should be registered.
    formatter = logging.Formatter("%(levelname)s")
    new_logger = ReportLogger(uniq_raw_logger, formatter=formatter)
    assert new_logger.formatter == formatter


# -- LoggerAdapter --


@pytest.mark.original_logger
def test_log_adapter_respects_log_level(caplog):
    # Preferably, in order to change log levels in tests `caplog.set_level`
    # should be used. However, this is the one test where we use
    # `logging.getLogger(DEFAULT_LOGGER).setLevel` to test the
    # behavior reported in the documentation. The wrapper object
    # `pyscaffold.log.logger` should respect the log level if the underlying
    # python logger object have changed.
    caplog.set_level(logging.NOTSET)

    possible_levels = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]

    for level in possible_levels:
        assert logger.wrapped == logging.getLogger(DEFAULT_LOGGER)
        # Given the logging level is set to INFO using `logging.getLogger`
        logging.getLogger(DEFAULT_LOGGER).setLevel(level)
        # Then the logger level should change accordingly
        assert logger.level == level

    # Trying to not leave a big logging level configuration behind
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.NOTSET)


def test_report(caplog, tmpfolder):
    # Given the logger level is properly configured
    caplog.set_level(logging.INFO)
    # When the report method is called,
    name = uniqstr()
    logger.report("make", str(tmpfolder.join(name)))
    # Then the message should be formatted accordingly.
    logs = caplog.text
    match = re.search("make.+" + name, logs)
    assert match
    # And relative paths should be used
    assert lp("/tmp") not in match.group(0)


def test_indent(caplog):
    # Given the logger level is set to INFO,
    caplog.set_level(logging.INFO)
    lg = logger.copy()  # Create a local copy to avoid shared state
    # And the nesting level is known
    nesting = lg.nesting
    # When the report method is called within an indentation context,
    name = uniqstr()
    with lg.indent():
        lg.report("make", name)
    # Then the spacing should be increased.
    assert any(
        match_report(
            r,
            activity="make",
            content=name,
            spacing=ReportFormatter.SPACING * (nesting + 2),
        )
        for r in caplog.records
    )

    # When report is called within a multi level indentation context,
    count = 5
    name = uniqstr()
    with lg.indent(count):
        lg.report("make", name)
    # Then the spacing should be increased accordingly.
    assert any(
        match_report(
            r,
            activity="make",
            content=name,
            spacing=ReportFormatter.SPACING * (nesting + count + 1),
        )
        for r in caplog.records
    )

    # When any other method is called with indentation,
    count = 3
    name = uniqstr()
    with lg.indent(count):
        lg.info(name)
    # Then the spacing should be added in the beginning
    logs = caplog.text
    assert (ReportFormatter.SPACING * (nesting + count) + name) in logs


def test_copy(caplog):
    # Given the logger level is set to INFO,
    caplog.set_level(logging.INFO)
    lg = logger.copy()  # Create a local copy to avoid shared state
    # And the nesting level is known
    nesting = lg.nesting
    # And a copy of the logger is made withing a context,
    count = 3
    with lg.indent(count):
        logger2 = lg.copy()
    # When the original logger indentation level is changed,
    name = uniqstr()
    with lg.indent(7):
        lg.report("make", "/some/report")
        # And the report method is called in the copy logger
        logger2.report("call", name)
        # Then the logging level should not be changed
        assert logger2.nesting == nesting + count

    # And the spacing should not be increased.
    assert any(
        match_report(
            r,
            activity="call",
            content=name,
            spacing=ReportFormatter.SPACING * (nesting + count + 1),
        )
        for r in caplog.records
    )


def test_reconfigure(monkeypatch, caplog, uniq_raw_logger):
    # Given an environment that supports color, and a restrictive logger
    caplog.set_level(logging.NOTSET)
    monkeypatch.setattr("pyscaffold.termui.supports_color", lambda *_: True)
    formatter = ReportFormatter()
    new_logger = ReportLogger(uniq_raw_logger, formatter=formatter, propagate=True)
    new_logger.level = logging.INFO
    # when the logger is reconfigured
    new_logger.reconfigure()
    name = uniqstr()
    # then the messages should be displayed and use colors
    new_logger.report("some1", name)
    out = caplog.messages[-1]
    assert re.search(ansi_pattern("some1") + ".+" + name, out)

    # when the logger is reconfigured with a higher level
    new_logger.reconfigure(log_level=logging.CRITICAL)
    # then the messages should not be displayed
    name = uniqstr()
    new_logger.report("some2", name)
    assert not re.search(ansi_pattern("some2") + ".+" + name, caplog.text)


def test_other_methods(caplog):
    # Given the logger level is properly set,
    caplog.set_level(logging.DEBUG)
    name = uniqstr()
    # When conventional methods are called on logger,
    logger.debug(name)
    # Then they should bypass `report`-specific formatting
    assert all(not match_report(r, message=name) for r in caplog.records)
    assert any(
        match_record(r, levelno=logging.DEBUG, message=name) for r in caplog.records
    )


# -- Formatter --


def test_create_padding():
    formatter = ReportFormatter()
    for text in ["abcd", "abcdefg", "ab"]:
        padding = formatter.create_padding(text)
        # Formatter should ensure activates are right padded
        assert len(padding + text) == formatter.ACTIVITY_MAXLEN


def parent_dir():
    return abspath(lp(".."))


def test_format_path():
    formatter = ReportFormatter()
    format = formatter.format_path
    # Formatter should abbrev paths but keep other subjects unchanged
    assert format("not a command") == "not a command"
    assert format("git commit") == "git commit"
    assert format("a random message") == "a random message"
    assert format(getcwd()) == "."
    assert format(lp("../dir/../dir/..")) == lp("..")
    assert format(lp("../dir/../dir/../foo")) == lp("../foo")
    # shorter absolute is better than relative
    assert format(lp("/a")) == lp("/a")


def test_format_target():
    formatter = ReportFormatter()
    format = formatter.format_target
    assert format(None) == ""
    assert format(getcwd()) == ""
    assert format(parent_dir()) == "to '..'"


def test_format_context():
    formatter = ReportFormatter()
    format = formatter.format_context
    assert format(None) == ""
    assert format(getcwd()) == ""
    assert format(parent_dir()) == "from '..'"


def test_format():
    formatter = ReportFormatter()

    def format(*args, **kwargs):
        return formatter.format(make_record(*args, **kwargs)).lstrip()

    assert format("run", "ls -lf .") == "run  ls -lf ."
    assert format("run", "ls", context=parent_dir()) == "run  ls from '..'"
    assert format(
        "copy", getcwd(), target=lp("../dir/../dir")
    ) == "copy  . to '{}'".format(lp("../dir"))
    fmt_out = format("create", lp("my/file"), nesting=1)
    assert fmt_out == f"create    {lp('my/file')}"


def test_colored_format_target():
    formatter = ColoredReportFormatter()
    format = formatter.format_target
    out = format(parent_dir())
    assert ColoredReportFormatter.TARGET_PREFIX in out
    assert ansi_regex("to").search(out)


def test_colored_format_context():
    formatter = ColoredReportFormatter()
    format = formatter.format_context
    out = format(parent_dir())
    assert ColoredReportFormatter.CONTEXT_PREFIX in out
    assert ansi_regex("from").search(out)


def test_colored_activity():
    formatter = ColoredReportFormatter()
    format = formatter.format_activity
    out = format("run")
    assert ansi_regex("run").search(out)


def test_colored_format():
    formatter = ColoredReportFormatter()

    def format(*args, **kwargs):
        return formatter.format(make_record(*args, **kwargs)).lstrip()

    out = format("invoke", "action")
    assert ansi_regex("invoke").search(out)
    assert ansi_regex("action").search(out)


def test_colored_report(tmpfolder, caplog, uniq_raw_logger):
    # Given the logger is properly set,
    uniq_raw_logger.setLevel(logging.INFO)
    formatter = ColoredReportFormatter()
    uniq_logger = ReportLogger(uniq_raw_logger, formatter=formatter, propagate=True)
    # When the report method is called,
    name = uniqstr()
    uniq_logger.report("make", str(tmpfolder.join(name)))
    # Then the message should contain activity surrounded by ansi codes,
    out = caplog.messages[-1]
    assert re.search(ansi_pattern("make") + ".+" + name, out)
    # And relative paths should be used
    assert lp("/tmp") not in out


def test_colored_others_methods(caplog, uniq_raw_logger):
    # Given the logger is properly set,
    uniq_raw_logger.setLevel(logging.DEBUG)
    formatter = ColoredReportFormatter()
    uniq_logger = ReportLogger(uniq_raw_logger, formatter=formatter, propagate=True)
    # When conventional methods are called on logger,
    name = uniqstr()
    uniq_logger.debug(name)
    # Then the message should be surrounded by ansi codes
    out = caplog.messages[-1]
    assert ansi_regex(name).search(out)
