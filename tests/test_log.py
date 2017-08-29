#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os import getcwd
from os.path import abspath

import pytest

from pyscaffold.log import (
    DEFAULT_LOGGER,
    ReportFormatter,
    ReportLogger,
    logger
)

from .log_helpers import last_log, make_record, match_last_report


@pytest.yield_fixture
def reset_handler():
    yield
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    for h in raw_logger.handlers:
        raw_logger.removeHandler(h)
    raw_logger.handlers = []
    new_logger = ReportLogger()
    assert len(raw_logger.handlers) == 1
    assert raw_logger.handlers[0] == new_logger.default_handler


def test_default_handler_registered():
    # When the module is imported,
    # Then a default handler should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    assert raw_logger.handlers
    assert raw_logger.handlers[0] == logger.default_handler


def test_pass_handler(reset_handler):
    # When the report logger is created with a handler
    new_logger = ReportLogger(handler=logging.NullHandler())
    assert isinstance(new_logger.default_handler, logging.NullHandler)


def test_default_formatter_registered():
    # When the module is imported,
    # Then a default formatter should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    handler = raw_logger.handlers[0]
    assert isinstance(handler.formatter, ReportFormatter)


def test_pass_formatter(reset_handler):
    # When the report logger is created with a handler
    formatter = logging.Formatter('%(levelname)s')
    new_logger = ReportLogger(formatter=formatter)
    assert new_logger.default_formatter == formatter


def test_report(caplog):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # When the report method is called,
    logger.report('make', '/some/report')
    # Then the message should be formatted accordingly.
    match = match_last_report(caplog)
    assert match['activity'] == 'make'
    assert match['content'] == '/some/report'


def test_indent(caplog):
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


def test_copy(caplog):
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


def test_other_methods(caplog):
    # Given the logger level is properly set,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.DEBUG)
    # When conventional methods are called on logger,
    logger.debug('some-info!')
    # Then they should bypass `report`-specific formatting
    match = match_last_report(caplog)
    assert not match
    assert caplog.records[-1].levelno == logging.DEBUG
    assert caplog.records[-1].message == 'some-info!'


formatter = ReportFormatter()


def test_create_padding():
    for text in ['abcd', 'abcdefg', 'ab']:
        padding = formatter.create_padding(text)
        # Formatter should ensure activates are right padded
        assert len(padding + text) == formatter.ACTIVITY_MAXLEN


def parent_dir():
    return abspath('..')


def test_format_path():
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
    format = formatter.format_target
    assert format(None) == ''
    assert format(getcwd()) == ''
    assert format(parent_dir()) == "to '..'"


def test_format_context():
    format = formatter.format_context
    assert format(None) == ''
    assert format(getcwd()) == ''
    assert format(parent_dir()) == "from '..'"


def test_format():
    def format(*args, **kwargs):
        return formatter.format(make_record(*args, **kwargs)).lstrip()

    assert format('run', 'ls -lf .') == 'run  ls -lf .'
    assert format('run', 'ls', context=parent_dir()) == "run  ls from '..'"
    assert (format('copy', getcwd(), target='../dir/../dir') ==
            "copy  . to '../dir'")
    assert format('create', 'my/file', nesting=1) == 'create    my/file'
