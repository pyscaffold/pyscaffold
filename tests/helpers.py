import logging
import os
import stat
from collections import namedtuple
from contextlib import contextmanager
from glob import glob
from pathlib import Path
from pprint import pformat
from shutil import rmtree
from time import sleep
from uuid import uuid4


def uniqstr():
    """Generates a unique random long string every time it is called"""
    return str(uuid4())


def uniqpath(nested=False):
    path = uniqstr()
    if nested:
        path.replace("-", "/")

    return Path(path)


def nop(*args, **kwargs):
    """Function that does nothing"""


def obj(**kwargs):
    """Create a generic object with the given fields"""
    constructor = namedtuple("GenericObject", kwargs.keys())
    return constructor(**kwargs)


def set_writable(func, path, exc_info):
    max_attempts = 10
    retry_interval = 0.1
    effective_ids = os.access in os.supports_effective_ids
    existing_files = glob("{}/*".format(path))

    if not os.access(path, os.W_OK, effective_ids=effective_ids):
        os.chmod(path, stat.S_IWUSR)
        return func(path)
    else:
        # For some weird reason we do have rights to remove the dir,
        # let's try again a few times more slowly (maybe a previous OS call
        # returned to the python interpreter but the files were not completely
        # removed yet?)
        for i in range(max_attempts):
            try:
                return rmtree(path)
            except OSError:
                sleep((i + 1) * retry_interval)

    logging.critical(
        "Something went wrong when removing %s. Contents:\n%s",
        path,
        pformat(existing_files),  # weirdly this is usually empty
        exc_info=exc_info,
    )
    (type_, value, traceback) = exc_info
    raise type_(value).with_traceback(traceback)


def command_exception(content):
    # Be lazy to import modules, so coverage has time to setup all the
    # required "probes"
    # (see @FlorianWilhelm comments on #174)
    from pyscaffold.exceptions import ShellCommandException

    return ShellCommandException(content)


@contextmanager
def temp_umask(umask):
    """Context manager that temporarily sets the process umask.

    Taken from Python's "private stdlib", module ``test.support``,
    license in https://github.com/python/cpython/blob/master/LICENSE.
    """
    oldmask = os.umask(umask)
    try:
        yield
    finally:
        os.umask(oldmask)
