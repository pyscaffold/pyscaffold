import pytest
import pkg_resources
from setuptools_scm import dump_version, get_version, PRETEND_KEY
from setuptools_scm.version import guess_next_version, meta, format_version


class MockTime(object):
    def __format__(self, *k):
        return 'time'


@pytest.mark.parametrize('tag, expected', [
    ('1.1', '1.2.dev0'),
    ('1.2.dev', '1.2.dev0'),
    ('1.1a2', '1.1a3.dev0'),
    ])
def test_next_tag(tag, expected):
    version = pkg_resources.parse_version(tag)
    assert guess_next_version(version, 0) == expected


VERSIONS = {
    'exact': meta('1.1', None, False),
    'zerodistance': meta('1.1', 0, False),
    'dirty': meta('1.1', None, True),
    'distance': meta('1.1', 3, False),
    'distancedirty': meta('1.1', 3, True),
}


@pytest.mark.parametrize('version,scheme,expected', [
    ('exact', 'guess-next-dev node-and-date', '1.1'),
    ('zerodistance', 'guess-next-dev node-and-date', '1.2.dev0+nNone'),
    ('dirty', 'guess-next-dev node-and-date', '1.2.dev0+nNone.dtime'),
    ('distance', 'guess-next-dev node-and-date', '1.2.dev3+nNone'),
    ('distancedirty', 'guess-next-dev node-and-date', '1.2.dev3+nNone.dtime'),
    ('exact', 'post-release node-and-date', '1.1'),
    ('zerodistance', 'post-release node-and-date', '1.1.post0+nNone'),
    ('dirty', 'post-release node-and-date', '1.1.post0+nNone.dtime'),
    ('distance', 'post-release node-and-date', '1.1.post3+nNone'),
    ('distancedirty', 'post-release node-and-date', '1.1.post3+nNone.dtime'),
])
def test_format_version(version, monkeypatch, scheme, expected):
    version = VERSIONS[version]
    monkeypatch.setattr(version, 'time', MockTime())
    vs, ls = scheme.split()
    assert format_version(
        version,
        version_scheme=vs,
        local_scheme=ls) == expected


def test_dump_version_doesnt_bail_on_value_error(tmpdir):
    write_to = "VERSION"
    version = str(VERSIONS['exact'].tag)
    with pytest.raises(ValueError) as exc_info:
        dump_version(tmpdir.strpath, version, write_to)
    assert str(exc_info.value).startswith("bad file format:")


def test_dump_version_works_with_pretend(tmpdir, monkeypatch):
    monkeypatch.setenv(PRETEND_KEY, '1.0')
    get_version(write_to=str(tmpdir.join('VERSION.txt')))
    assert tmpdir.join('VERSION.txt').read() == '1.0'
