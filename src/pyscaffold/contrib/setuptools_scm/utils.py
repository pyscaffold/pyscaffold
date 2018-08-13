"""
utils
"""
from __future__ import print_function, unicode_literals
import inspect
import warnings
import sys
import shlex
import subprocess
import os
import io
import platform


DEBUG = bool(os.environ.get("SETUPTOOLS_SCM_DEBUG"))
IS_WINDOWS = platform.system() == "Windows"
PY2 = sys.version_info < (3,)
PY3 = sys.version_info > (3,)
string_types = (str,) if PY3 else (str, unicode)  # noqa


def trace(*k):
    if DEBUG:
        print(*k)
        sys.stdout.flush()


def ensure_stripped_str(str_or_bytes):
    if isinstance(str_or_bytes, str):
        return str_or_bytes.strip()
    else:
        return str_or_bytes.decode("utf-8", "surrogateescape").strip()


def _always_strings(env_dict):
    """
    On Windows and Python 2, environment dictionaries must be strings
    and not unicode.
    """
    if IS_WINDOWS or PY2:
        env_dict.update((key, str(value)) for (key, value) in env_dict.items())
    return env_dict


def _popen_pipes(cmd, cwd):

    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(cwd),
        env=_always_strings(
            dict(
                os.environ,
                # try to disable i18n
                LC_ALL="C",
                LANGUAGE="",
                HGPLAIN="1",
            )
        ),
    )


def do_ex(cmd, cwd="."):
    trace("cmd", repr(cmd))
    if os.name == "posix" and not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    p = _popen_pipes(cmd, cwd)
    out, err = p.communicate()
    if out:
        trace("out", repr(out))
    if err:
        trace("err", repr(err))
    if p.returncode:
        trace("ret", p.returncode)
    return ensure_stripped_str(out), ensure_stripped_str(err), p.returncode


def do(cmd, cwd="."):
    out, err, ret = do_ex(cmd, cwd)
    if ret:
        print(err)
    return out


def data_from_mime(path):
    with io.open(path, encoding="utf-8") as fp:
        content = fp.read()
    trace("content", repr(content))
    # the complex conditions come from reading pseudo-mime-messages
    data = dict(x.split(": ", 1) for x in content.splitlines() if ": " in x)
    trace("data", data)
    return data


def function_has_arg(fn, argname):
    assert inspect.isfunction(fn)

    if PY2:
        argspec = inspect.getargspec(fn).args
    else:
        argspec = inspect.getfullargspec(fn).args

    return argname in argspec


def has_command(name):
    try:
        p = _popen_pipes([name, "help"], ".")
    except OSError:
        trace(*sys.exc_info())
        res = False
    else:
        p.communicate()
        res = not p.returncode
    if not res:
        warnings.warn("%r was not found" % name)
    return res
