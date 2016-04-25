from __future__ import print_function
import datetime
import re
from .utils import trace

from pkg_resources import iter_entry_points

from distutils import log

try:
    from pkg_resources import parse_version, SetuptoolsVersion
except ImportError as e:
    parse_version = SetuptoolsVersion = None


def _warn_if_setuptools_outdated():
    if parse_version is None:
        log.warn("your setuptools is too old (<12)")
        log.warn("setuptools_scm functionality is degraded")


def callable_or_entrypoint(group, callable_or_name):
    trace('ep', (group, callable_or_name))
    if isinstance(callable_or_name, str):
        for ep in iter_entry_points(group, callable_or_name):
            return ep.load()
    else:
        return callable_or_name


def tag_to_version(tag):
    trace('tag', tag)
    # lstrip the v because of py2/py3 differences in setuptools
    # also required for old versions of setuptools
    version = tag.rsplit('-', 1)[-1].lstrip('v')
    if parse_version is None:
        return version
    version = parse_version(version)
    trace('version', repr(version))
    if isinstance(version, SetuptoolsVersion):
        return version


def tags_to_versions(tags):
    versions = map(tag_to_version, tags)
    return [v for v in versions if v is not None]


class ScmVersion(object):
    def __init__(self, tag_version,
                 distance=None, node=None, dirty=False,
                 **kw):
        self.tag = tag_version
        if dirty and distance is None:
            distance = 0
        self.distance = distance
        self.node = node
        self.time = datetime.datetime.now()
        self.extra = kw
        self.dirty = dirty

    @property
    def exact(self):
        return self.distance is None

    def __repr__(self):
        return self.format_with(
            '<ScmVersion {tag} d={distance}'
            ' n={node} d={dirty} x={extra}>')

    def format_with(self, fmt):
        return fmt.format(
            time=self.time,
            tag=self.tag, distance=self.distance,
            node=self.node, dirty=self.dirty, extra=self.extra)

    def format_choice(self, clean_format, dirty_format):
        return self.format_with(dirty_format if self.dirty else clean_format)


def meta(tag, distance=None, dirty=False, node=None, **kw):
    if SetuptoolsVersion is None or not isinstance(tag, SetuptoolsVersion):
        tag = tag_to_version(tag)
    trace('version', tag)

    assert tag is not None, 'cant parse version %s' % tag
    return ScmVersion(tag, distance, node, dirty, **kw)


def guess_next_version(tag_version, distance):
    version = str(tag_version)
    if '.dev' in version:
        prefix, tail = version.rsplit('.dev', 1)
        assert tail == '0', 'own dev numbers are unsupported'
        return '%s.dev%s' % (prefix, distance)
    else:
        prefix, tail = re.match('(.*?)(\d+)$', version).groups()
        return '%s%d.dev%s' % (prefix, int(tail) + 1, distance)


def guess_next_dev_version(version):
    if version.exact:
        return version.format_with("{tag}")
    else:
        return guess_next_version(version.tag, version.distance)


def get_local_node_and_date(version):
    if version.exact:
        return version.format_choice("", "+d{time:%Y%m%d}")
    else:
        return version.format_choice("+n{node}", "+n{node}.d{time:%Y%m%d}")


def get_local_dirty_tag(version):
    return version.format_choice('', '+dirty')


def postrelease_version(version):
    if version.exact:
        return version.format_with('{tag}')
    else:
        return version.format_with('{tag}.post{distance}')


def format_version(version, **config):
    trace('scm version', version)
    trace('config', config)
    version_scheme = callable_or_entrypoint(
        'setuptools_scm.version_scheme', config['version_scheme'])
    local_scheme = callable_or_entrypoint(
        'setuptools_scm.local_scheme', config['local_scheme'])
    main_version = version_scheme(version)
    trace('version', main_version)
    local_version = local_scheme(version)
    trace('local_version', local_version)
    return version_scheme(version) + local_scheme(version)
