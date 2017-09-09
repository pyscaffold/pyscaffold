from __future__ import print_function
import datetime
import warnings
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
            trace("ep found:", ep.name)
            return ep.load()
    else:
        return callable_or_name


def tag_to_version(tag):
    trace('tag', tag)
    if '+' in tag:
        warnings.warn("tag %r will be stripped of the local component" % tag)
        tag = tag.split('+')[0]
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
                 preformatted=False,
                 **kw):
        if kw:
            trace("unknown args", kw)
        self.tag = tag_version
        if dirty and distance is None:
            distance = 0
        self.distance = distance
        self.node = node
        self.time = datetime.datetime.now()
        self.extra = kw
        self.dirty = dirty
        self.preformatted = preformatted

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


def _parse_tag(tag, preformatted):
    if preformatted:
        return tag
    if SetuptoolsVersion is None or not isinstance(tag, SetuptoolsVersion):
        tag = tag_to_version(tag)
    return tag


def meta(tag, distance=None, dirty=False, node=None, preformatted=False, **kw):
    tag = _parse_tag(tag, preformatted)
    trace('version', tag)
    assert tag is not None, 'cant parse version %s' % tag
    return ScmVersion(tag, distance, node, dirty, preformatted, **kw)


def guess_next_version(tag_version, distance):
    version = _strip_local(str(tag_version))
    bumped = _bump_dev(version) or _bump_regex(version)
    suffix = '.dev%s' % distance
    return bumped + suffix


def _strip_local(version_string):
    public, sep, local = version_string.partition('+')
    return public


def _bump_dev(version):
    if '.dev' not in version:
        return

    prefix, tail = version.rsplit('.dev', 1)
    assert tail == '0', 'own dev numbers are unsupported'
    return prefix


def _bump_regex(version):
    prefix, tail = re.match('(.*?)(\d+)$', version).groups()
    return '%s%d' % (prefix, int(tail) + 1)


def guess_next_dev_version(version):
    if version.exact:
        return version.format_with("{tag}")
    else:
        return guess_next_version(version.tag, version.distance)


def get_local_node_and_date(version):
    if version.exact or version.node is None:
        return version.format_choice("", "+d{time:%Y%m%d}")
    else:
        return version.format_choice("+{node}", "+{node}.d{time:%Y%m%d}")


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
    if version.preformatted:
        return version.tag
    version_scheme = callable_or_entrypoint(
        'setuptools_scm.version_scheme', config['version_scheme'])
    local_scheme = callable_or_entrypoint(
        'setuptools_scm.local_scheme', config['local_scheme'])
    main_version = version_scheme(version)
    trace('version', main_version)
    local_version = local_scheme(version)
    trace('local_version', local_version)
    return version_scheme(version) + local_scheme(version)
