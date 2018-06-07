#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
from os import getcwd
from os.path import abspath

import pytest

from pyscaffold.log import (
    DEFAULT_LOGGER,
    ColoredReportFormatter,
    ReportFormatter,
    ReportLogger,
    logger,
    configure_logger
)

from .log_helpers import (
    ansi_regex,
    ansi_pattern,
    make_record,
    match_record,
    match_report,
    random_time_based_string as uniqstr
)


@pytest.fixture
def uniq_raw_logger():
    return logging.getLogger(uniqstr())


@pytest.fixture
def uniq_logger(uniq_raw_logger):
    return ReportLogger(uniq_raw_logger)


def test_default_handler_registered():
    # When the module is imported,
    # Then a default handler should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    assert raw_logger.handlers
    assert raw_logger.handlers[0] == logger.handler


def test_pass_handler(uniq_raw_logger):
    # When the report logger is created with a handler
    new_logger = ReportLogger(uniq_raw_logger, handler=logging.NullHandler())
    assert isinstance(new_logger.handler, logging.NullHandler)


def test_default_formatter_registered():
    # When the module is imported,
    # Then a default formatter should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    handler = raw_logger.handlers[0]
    assert isinstance(handler.formatter, ReportFormatter)


def test_pass_formatter(uniq_raw_logger):
    # When the report logger is created with a formatter
    # Then that formatter should be registered.
    formatter = logging.Formatter('%(levelname)s')
    new_logger = ReportLogger(uniq_raw_logger, formatter=formatter)
    assert new_logger.formatter == formatter


def test_report(caplog, tmpfolder):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # When the report method is called,
    name = uniqstr()
    logger.report('make', str(tmpfolder.join(name)))
    # Then the message should be formatted accordingly.
    logs = caplog.text
    assert re.search('make.+' + name, logs)
    assert any(
        match_report(r, activity='make', content=name)
        for r in caplog.records
    )
    # And relative paths should be used
    assert '/tmp' not in logs


def test_indent(caplog):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    lg = logger.copy()  # Create a local copy to avoid shared state
    # And the nesting level is known
    nesting = lg.nesting
    # When the report method is called within an indentation context,
    name = uniqstr()
    with lg.indent():
        lg.report('make', name)
    # Then the spacing should be increased.
    assert any(
        match_report(r, activity='make', content=name,
                     spacing=ReportFormatter.SPACING * (nesting + 2))
        for r in caplog.records
    )

    # When report is called within a multi level indentation context,
    count = 5
    name = uniqstr()
    with lg.indent(count):
        lg.report('make', name)
    # Then the spacing should be increased accordingly.
    assert any(
        match_report(r, activity='make', content=name,
                     spacing=ReportFormatter.SPACING * (nesting + count + 1))
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
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    lg = logger.copy()  # Create a local copy to avoid shared state
    # And the nesting level is known
    nesting = logger.nesting
    # And a copy of the logger is made withing a context,
    count = 3
    with lg.indent(count):
        logger2 = lg.copy()
    # When the original logger indentation level is changed,
    name = uniqstr()
    with lg.indent(7):
        lg.report('make', '/some/report')
        # And the report method is called in the copy logger
        logger2.report('call', name)
        # Then the logging level should not be changed
        assert logger2.nesting == nesting + count

    # And the spacing should not be increased.
    assert any(
        match_report(r, activity='call', content=name,
                     spacing=ReportFormatter.SPACING * (nesting + count + 1))
        for r in caplog.records
    )


def test_other_methods(caplog):
    # Given the logger level is properly set,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.DEBUG)
    name = uniqstr()
    # When conventional methods are called on logger,
    logger.debug(name)
    # Then they should bypass `report`-specific formatting
    assert all(
        not match_report(r, message=name)
        for r in caplog.records
    )
    assert any(
        match_record(r, levelno=logging.DEBUG, message=name)
        for r in caplog.records
    )


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


def test_colored_report(tmpfolder, caplog, uniq_raw_logger):
    # Given the logger is properly set,
    uniq_raw_logger.setLevel(logging.INFO)
    uniq_logger = ReportLogger(uniq_raw_logger,
                               formatter=ColoredReportFormatter())
    # When the report method is called,
    name = uniqstr()
    uniq_logger.report('make', str(tmpfolder.join(name)))
    # Then the message should contain activity surrounded by ansi codes,
    out = caplog.text
    assert re.search(ansi_pattern('make') + '.+' + name, out)
    # And relative paths should be used
    assert '/tmp' not in out


def test_colored_others_methods(caplog, uniq_raw_logger):
    # Given the logger is properly set,
    uniq_raw_logger.setLevel(logging.DEBUG)
    uniq_logger = ReportLogger(uniq_raw_logger,
                               formatter=ColoredReportFormatter())
    # When conventional methods are called on logger,
    name = uniqstr()
    uniq_logger.debug(name)
    # Then the message should be surrounded by ansi codes
    out = caplog.text
    assert ansi_regex(name).search(out)


def test_configure_logger(monkeypatch, caplog):
    # Given an environment that supports color,
    monkeypatch.setattr('pyscaffold.termui.supports_color', lambda *_: True)
    # when configure_logger in called,
    opts = dict(log_level=logging.INFO)
    configure_logger(opts)
    # then the formatter should be changed to use colors,
    name = uniqstr()
    logger.report('some', name)
    out = caplog.text
    assert re.search(ansi_pattern('some') + '.+' + name, out)
