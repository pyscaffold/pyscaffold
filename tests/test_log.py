#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
from collections import defaultdict

from pyscaffold.log import DEFAULT_LOGGER, ReportFormatter, logger


def test_default_handler_registered():
    # When the module is imported,
    # Then a default handler should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    assert raw_logger.handlers
    assert raw_logger.handlers[0] == logger.default_handler


def test_default_formatter_registered():
    # When the module is imported,
    # Then a default formatter should be registered.
    raw_logger = logging.getLogger(DEFAULT_LOGGER)
    handler = raw_logger.handlers[0]
    assert isinstance(handler.formatter, ReportFormatter)


REPORT_REGEX = re.compile(
    '^\s*(?P<activity>\w+)(?P<spacing>\s+)(?P<subject>\S+)$', re.I + re.U)


def match_last_report(log):
    result = REPORT_REGEX.search(log.records[-1].message)
    return result.groupdict() if result else defaultdict(lambda: None)


def test_report(caplog):
    # Given the logger level is set to INFO,
    logging.getLogger(DEFAULT_LOGGER).setLevel(logging.INFO)
    # When the report method is called,
    logger.report('make', '/some/report')
    # Then the message should be formatted accordingly.
    match = match_last_report(caplog)
    assert match
    assert match['activity'] == 'make'
    assert match['subject'] == '/some/report'


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
