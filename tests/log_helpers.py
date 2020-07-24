import logging
import re


def find_report(log, activity, subject):
    """Check if an activity was logged."""
    for record in log.records:
        if record.activity == activity and str(subject) in str(record.subject):
            return record

    return False


def make_record(activity, subject, context=None, target=None, nesting=0):
    """Create a custom record."""
    return logging.makeLogRecord(
        dict(
            activity=activity,
            subject=subject,
            context=context,
            target=target,
            nesting=nesting,
        )
    )


def match_record(record, **kwargs):
    for key, value in kwargs.items():
        if getattr(record, key) != value:
            return False

    return record


REPORT_REGEX = re.compile(
    r"^\s*(?P<activity>\w+)(?P<spacing>\s+)(?P<content>.+)$", re.I + re.U
)


def match_report(record, message=None, **kwargs):
    """Check if a log entry was created using `report`, and compare."""
    result = REPORT_REGEX.search(record.message)
    if not result:
        return False

    if message is not None and message not in record.message:
        return False

    match = result.groupdict()

    for key, value in kwargs.items():
        if match[key] != value:
            return False

    return match


def ansi_pattern(text):
    return r"({prefix}\[\d+m)+{text}{prefix}\[0m".format(
        text=re.escape(text), prefix="\033"
    )


def ansi_regex(text):
    return re.compile(ansi_pattern(text), re.I)
