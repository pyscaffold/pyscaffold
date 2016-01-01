import os
import itertools
import pytest

os.environ['SETUPTOOLS_SCM_DEBUG'] = '1'
VERSION_PKGS = ['setuptools', 'setuptools_scm']


def pytest_report_header():
    import pkg_resources
    res = []
    for pkg in VERSION_PKGS:
        version = pkg_resources.get_distribution(pkg).version
        res.append('%s version %s' % (pkg, version))
    return res


class Wd(object):
    commit_command = None
    add_command = None

    def __init__(self, cwd):
        self.cwd = cwd
        self.__counter = itertools.count()

    def __call__(self, cmd, **kw):
        if kw:
            cmd = cmd.format(**kw)
        from setuptools_scm.utils import do
        return do(cmd, self.cwd)

    def write(self, name, value, **kw):
        filename = self.cwd.join(name)
        if kw:
            value = value.format(**kw)
        filename.write(value)
        return filename

    def _reason(self, given_reason):
        if given_reason is None:
            return 'number-{c}'.format(c=next(self.__counter))
        else:
            return given_reason

    def commit(self, reason=None):
        reason = self._reason(reason)
        self(self.commit_command, reason=reason)

    def commit_testfile(self, reason=None):
        reason = self._reason(reason)
        self.write('test.txt', 'test {reason}', reason=reason)
        self(self.add_command)
        self.commit(reason=reason)

    @property
    def version(self):
        __tracebackhide__ = True
        from setuptools_scm import get_version
        version = get_version(root=str(self.cwd))
        print(version)
        return version


@pytest.fixture
def wd(tmpdir):
    return Wd(tmpdir)
