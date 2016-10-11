"""
utils
"""
from __future__ import print_function, unicode_literals
import sys
import shlex
import subprocess
import os
import io
import platform


DEBUG = bool(os.environ.get("SETUPTOOLS_SCM_DEBUG"))


def trace(*k):
    if DEBUG:
        print(*k)
        sys.stdout.flush()


def ensure_stripped_str(str_or_bytes):
    if isinstance(str_or_bytes, str):
        return str_or_bytes.strip()
    else:
        return str_or_bytes.decode('utf-8', 'surogate_escape').strip()


def _always_strings(env_dict):
    """
    On Windows and Python 2, environment dictionaries must be strings
    and not unicode.
    """
    is_windows = platform.system == 'Windows'
    PY2 = sys.version_info < (3,)
    if is_windows or PY2:
        env_dict.update(
            (key, str(value))
            for (key, value) in env_dict.items()
        )
    return env_dict


def do_ex(cmd, cwd='.'):
    trace('cmd', repr(cmd))
    if not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(cwd),
        env=_always_strings(dict(
            os.environ,
            # try to disable i18n
            LC_ALL='C',
            LANGUAGE='',
            HGPLAIN='1',
        ))
    )

    out, err = p.communicate()
    if out:
        trace('out', repr(out))
    if err:
        trace('err', repr(err))
    if p.returncode:
        trace('ret', p.returncode)
    return ensure_stripped_str(out), ensure_stripped_str(err), p.returncode


def do(cmd, cwd='.'):
    out, err, ret = do_ex(cmd, cwd)
    if ret:
        print(err)
    return out


def data_from_mime(path):
    with io.open(path, encoding='utf-8') as fp:
        content = fp.read()
    trace('content', repr(content))
    # the complex conditions come from reading pseudo-mime-messages
    data = dict(
        x.split(': ', 1)
        for x in content.splitlines()
        if ': ' in x)
    trace('data', data)
    return data
