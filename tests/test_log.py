#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os import getcwd
from os.path import abspath

from pyscaffold.log import (
    DEFAULT_LOGGER,
    ColoredReportFormatter,
    ReportFormatter,
    ReportLogger,
    logger,
    configure_logger
)

from .log_helpers import ansi_regex, last_log, make_record, match_last_report


def test_default_handler_registered():
    # When the module is imported,
    # Then a default handler should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    assert raw_logger.handlers
    assert raw_logger.handlers[0] == logger.handler


def test_pass_handler(reset_logger):
    # When the report logger is created with a handler
    new_logger = ReportLogger(handler=logging.NullHandler())
    assert isinstance(new_logger.handler, logging.NullHandler)


def test_default_formatter_registered():
    # When the module is imported,
    # Then a default formatter should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    handler = raw_logger.handlers[0]
    assert isinstance(handler.formatter, ReportFormatter)


def test_pass_formatter(reset_logger):
    # When the report logger is created with a handler
    formatter = logging.Formatter('%(levelname)s')
    new_logger = ReportLogger(formatter=formatter)
    assert new_logger.formatter == formatter


def test_report(tmpfolder, caplog, reset_logger):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # When the report method is called,
    logger.report('make', str(tmpfolder) + '/some/report')
    # Then the message should be formatted accordingly.
    match = match_last_report(caplog)
    assert match['activity'] == 'make'
    assert match['content'] == 'some/report'
    # And relative paths should be used
    out = caplog.text
    assert '/tmp' not in out
    assert 'some/report' in out


def test_indent(caplog, reset_logger):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # And the nesting level is not changed
    assert logger.nesting == 0
    # When the report method is called within an indentation context,
    with logger.indent():
        logger.report('make', '/some/report')
    # Then the spacing should be increased.
    match = match_last_report(caplog)
    assert match['spacing'] == ReportFormatter.SPACING * 2

    # When report is called within a multi level indentation context,
    count = 5
    with logger.indent(count):
        logger.report('make', '/some/report')
    # Then the spacing should be increased accordingly.
    match = match_last_report(caplog)
    assert match['spacing'] == ReportFormatter.SPACING * (count + 1)

    # When any other method is called with indentation,
    count = 3
    with logger.indent(count):
        logger.info('something')
    # Then the spacing should be added in the beginning
    assert (ReportFormatter.SPACING * count + 'something') in last_log(caplog)


def test_copy(caplog, reset_logger):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # And the nesting level is not changed
    assert logger.nesting == 0
    # And a copy of the logger is made withing a context,
    count = 3
    with logger.indent(count):
        logger2 = logger.copy()
    # When the original logger indentation level is changed,
    with logger.indent(7):
        logger.report('make', '/some/report')
        # And the report method is called in the clone logger
        logger2.report('call', '/other/logger')

    # Then the spacing should not be increased.
    match = match_last_report(caplog)
    assert match['spacing'] == ReportFormatter.SPACING * (count + 1)


def test_other_methods(caplog, reset_logger):
    # Given the logger level is properly set,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.DEBUG)
    # When conventional methods are called on logger,
    logger.debug('some-info!')
    # Then they should bypass `report`-specific formatting
    match = match_last_report(caplog)
    assert not match
    assert caplog.records[-1].levelno == logging.DEBUG
    assert caplog.records[-1].message == 'some-info!'


def test_create_padding():
    formatter = ReportFormatter()
    for text in ['abcd', 'abcdefg', 'ab']:
        padding = formatter.create_padding(text)
        # Formatter should ensure activates are right padded
        assert len(padding + text) == formatter.ACTIVITY_MAXLEN


def parent_dir():
    return abspath('..')


def test_format_path():
    formatter = ReportFormatter()
    format = formatter.format_path
    # Formatter should abbrev paths but keep other subjects unchanged
    assert format('not a command') == 'not a command'
    assert format('git commit') == 'git commit'
    assert format('a random message') == 'a random message'
    assert format(getcwd()) == '.'
    assert format('../dir/../dir/..') == '..'
    assert format('../dir/../dir/../foo') == '../foo'
    assert format('/a') == '/a'  # shorter absolute is better than relative


def test_format_target():
    formatter = ReportFormatter()
    format = formatter.format_target
    assert format(None) == ''
    assert format(getcwd()) == ''
    assert format(parent_dir()) == "to '..'"


def test_format_context():
    formatter = ReportFormatter()
    format = formatter.format_context
    assert format(None) == ''
    assert format(getcwd()) == ''
    assert format(parent_dir()) == "from '..'"


def test_format():
    formatter = ReportFormatter()

    def format(*args, **kwargs):
        return formatter.format(make_record(*args, **kwargs)).lstrip()

    assert format('run', 'ls -lf .') == 'run  ls -lf .'
    assert format('run', 'ls', context=parent_dir()) == "run  ls from '..'"
    assert (format('copy', getcwd(), target='../dir/../dir') ==
            "copy  . to '../dir'")
    assert format('create', 'my/file', nesting=1) == 'create    my/file'


def test_colored_format_target():
    formatter = ColoredReportFormatter()
    format = formatter.format_target
    out = format(parent_dir())
    assert ColoredReportFormatter.TARGET_PREFIX in out
    assert ansi_regex('to').search(out)


def test_colored_format_context():
    formatter = ColoredReportFormatter()
    format = formatter.format_context
    out = format(parent_dir())
    assert ColoredReportFormatter.CONTEXT_PREFIX in out
    assert ansi_regex('from').search(out)


def test_colored_activity():
    formatter = ColoredReportFormatter()
    format = formatter.format_activity
    out = format('run')
    assert ansi_regex('run').search(out)


def test_colored_format():
    formatter = ColoredReportFormatter()

    def format(*args, **kwargs):
        return formatter.format(make_record(*args, **kwargs)).lstrip()

    out = format('invoke', 'action')
    assert ansi_regex('invoke').search(out)
    assert ansi_regex('action').search(out)


def test_colored_report(tmpfolder, caplog, reset_logger):
    # Given the logger is properly set,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    logger.handler.setFormatter(ColoredReportFormatter())
    # When the report method is called,
    logger.report('make', str(tmpfolder) + '/some/report')
    # Then the message should contain activity surrounded by ansi codes,
    out = caplog.text
    assert ansi_regex('make').search(out)
    # And relative paths should be used
    assert '/tmp' not in out
    assert 'some/report' in out


def test_colored_others_methods(caplog, reset_logger):
    # Given the logger is properly set,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.DEBUG)
    logger.handler.setFormatter(ColoredReportFormatter())
    # When conventional methods are called on logger,
    logger.debug('some-info!')
    # Then the message should be surrounded by ansi codes
    out = caplog.text
    assert ansi_regex('some-info!').search(out)


def test_configure_logger(monkeypatch, caplog, reset_logger):
    # Given an environment that supports color,
    monkeypatch.setattr('pyscaffold.termui.supports_color', lambda *_: True)
    # when configure_logger in called,
    opts = dict(log_level=logging.INFO)
    configure_logger(opts)
    # then the formatter should be changed to use colors,
    logger.report('some', 'activity')
    out = caplog.text
    assert ansi_regex('some').search(out)
