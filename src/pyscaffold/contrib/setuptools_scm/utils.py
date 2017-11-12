"""
utils
"""
from __future__ import print_function, unicode_literals
import warnings
import sys
import shlex
import subprocess
import os
from os.path import abspath, normcase, realpath
import io
import platform


DEBUG = bool(os.environ.get("SETUPTOOLS_SCM_DEBUG"))
IS_WINDOWS = platform.system() == 'Windows'
PY2 = sys.version_info < (3,)


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
    if IS_WINDOWS or PY2:
        env_dict.update(
            (key, str(value))
            for (key, value) in env_dict.items()
        )
    return env_dict


def _popen_pipes(cmd, cwd):

    return subprocess.Popen(
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


def do_ex(cmd, cwd='.'):
    trace('cmd', repr(cmd))
    if not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    p = _popen_pipes(cmd, cwd)
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


def has_command(name):
    try:
        p = _popen_pipes([name, 'help'], '.')
    except OSError:
        trace(*sys.exc_info())
        res = False
    else:
        p.communicate()
        res = not p.returncode
    if not res:
        warnings.warn("%r was not found" % name)
    return res


def _normalized(path):
    if IS_WINDOWS:
        path = get_windows_long_path_name(path)
    return normcase(abspath(realpath(path)))


if IS_WINDOWS:
    from ctypes import create_unicode_buffer, windll, WinError
    from ctypes.wintypes import MAX_PATH, LPCWSTR, LPWSTR, DWORD

    GetLongPathNameW = windll.kernel32.GetLongPathNameW
    GetLongPathNameW.argtypes = [LPCWSTR, LPWSTR, DWORD]
    GetLongPathNameW.restype = DWORD

    def get_windows_long_path_name(path):
        """
        Converts the specified path from short (MS-DOS style) to long form
        using the 'GetLongPathNameW' function from Windows API.

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa364980(v=vs.85).aspx
        """
        if PY2:
            # decode path using filesystem encoding on python2; on python3
            # it is already a unicode string
            path = unicode(path, sys.getfilesystemencoding())  # noqa

        pathlen = MAX_PATH + 1
        if DEBUG:
            # test reallocation logic
            pathlen = 1

        for _ in range(2):
            buf = create_unicode_buffer(pathlen)
            retval = GetLongPathNameW(path, buf, pathlen)

            if retval == 0:
                # if the function fails for any reason (e.g. file does not
                # exist), the return value is zero
                raise WinError()

            if retval <= pathlen:
                # the function succeeded: the return value is the length of
                # the string copied to the buffer
                if PY2:
                    # re-encode to native 'str' type (i.e. bytes) on python2
                    return buf.value.encode(sys.getfilesystemencoding())
                return buf.value

            # if the buffer is too small to contain the result, the return
            # value is the size of the buffer required to hold the path and
            # the terminating NULL char; we retry using a large enough buffer
            pathlen = retval

        raise RuntimeError("Failed to get long path name: {!r}".format(path))
