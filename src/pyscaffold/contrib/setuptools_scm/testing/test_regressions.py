import sys
import subprocess

from setuptools_scm import get_version
from setuptools_scm.git import parse
from setuptools_scm.utils import do_ex, do

import pytest


def test_pkginfo_noscmroot(tmpdir, monkeypatch):
    """if we are indeed a sdist, the root does not apply"""
    monkeypatch.delenv("SETUPTOOLS_SCM_DEBUG")

    # we should get the version from pkg-info if git is broken
    p = tmpdir.ensure('sub/package', dir=1)
    tmpdir.mkdir('.git')
    p.join('setup.py').write(
        'from setuptools import setup;'
        'setup(use_scm_version={"root": ".."})')

    _, stderr, ret = do_ex((sys.executable, 'setup.py', '--version'), p)
    assert 'setuptools-scm was unable to detect version for' in stderr
    assert ret == 1

    p.join("PKG-INFO").write('Version: 1.0')
    res = do((sys.executable, 'setup.py', '--version'), p)
    assert res == '1.0'

    do('git init', p.dirpath())
    res = do((sys.executable, 'setup.py', '--version'), p)
    assert res == '1.0'


def test_pip_egg_info(tmpdir, monkeypatch):
    """if we are indeed a sdist, the root does not apply"""

    # we should get the version from pkg-info if git is broken
    p = tmpdir.ensure('sub/package', dir=1)
    tmpdir.mkdir('.git')
    p.join('setup.py').write(
        'from setuptools import setup;'
        'setup(use_scm_version={"root": ".."})')

    with pytest.raises(LookupError):
        get_version(root=p.strpath)

    p.ensure('pip-egg-info/random.egg-info/PKG-INFO').write('Version: 1.0')
    assert get_version(root=p.strpath) == '1.0'


@pytest.mark.issue(164)
def test_pip_download(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    subprocess.check_call([
        sys.executable, '-c',
        'import pip;pip.main()', 'download', 'lz4==0.9.0',
    ])


def test_use_scm_version_callable(tmpdir, monkeypatch):
    """use of callable as use_scm_version argument"""
    monkeypatch.delenv("SETUPTOOLS_SCM_DEBUG")

    p = tmpdir.ensure('sub/package', dir=1)
    p.join('setup.py').write(
        '''from setuptools import setup
def vcfg():
    from setuptools_scm.version import guess_next_dev_version
    def vs(v):
        return guess_next_dev_version(v)
    return {"version_scheme": vs}
setup(use_scm_version=vcfg)
''')
    p.join("PKG-INFO").write('Version: 1.0')

    res = do((sys.executable, 'setup.py', '--version'), p)
    assert res == '1.0'


@pytest.mark.skipif(sys.platform != 'win32',
                    reason="this bug is only valid on windows")
def test_case_mismatch_on_windows_git(tmpdir):
    """Case insensitive path checks on Windows"""
    p = tmpdir.ensure("CapitalizedDir", dir=1)

    do('git init', p)
    res = parse(str(p).lower())
    assert res is not None
