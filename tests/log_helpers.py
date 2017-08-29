#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
from collections import defaultdict


def clear_log(log):
    log.handler.records = []


def last_log(log):
    return log.records[-1].message


def find_report(log, activity, subject):
    """Check if an activity was logged."""
    for record in log.records:
        if record.activity == activity and subject in record.subject:
            return record

    return False


def make_record(activity, subject, context=None, target=None, nesting=0):
    """Create a custom record."""
    return logging.makeLogRecord(dict(
        activity=activity,
        subject=subject,
        context=context,
        target=target,
        nesting=nesting
    ))


REPORT_REGEX = re.compile(
    r'^\s*(?P<activity>\w+)(?P<spacing>\s+)(?P<content>.+)$', re.I + re.U)


def match_last_report(log):
    """Check if the last log entry was created using `report` and parse it."""
    result = REPORT_REGEX.search(log.records[-1].message)
    return result.groupdict() if result else defaultdict(lambda: None)


def ansi_regex(text):
    return re.compile(r'({prefix}\[\d+m)+{text}{prefix}\[0m'.format(
        text=re.escape(text), prefix='\033'), re.I)
