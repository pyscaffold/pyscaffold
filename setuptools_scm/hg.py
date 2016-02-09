import os
from .utils import do, trace, data_from_mime
from .version import meta, tags_to_versions

FILES_COMMAND = 'hg locate -I .'


def _hg_tagdist_normalize_tagcommit(root, tag, dist, node):
    dirty = node.endswith('+')
    node = node.strip('+')
    st = do('hg st --no-status --change %s' % str(node), root)

    trace('normalize', locals())
    if int(dist) == 1 and st == '.hgtags' and not dirty:
        return meta(tag)
    else:
        return meta(tag, distance=dist, node=node, dirty=dirty)


def parse(root):
    l = do('hg id -i -t', root).split()
    node = l.pop(0)
    tags = tags_to_versions(l)
    # filter tip in degraded mode on old setuptools
    tags = [x for x in tags if x != 'tip']
    dirty = node[-1] == '+'
    if tags:
        return meta(tags[0], dirty=dirty)

    if node.strip('+') == '0'*12:
        trace('initial node', root)
        return meta('0.0', dirty=dirty)

    # the newline is needed for merge stae, see issue 72
    cmd = 'hg parents --template "{latesttag} {latesttagdistance}\n"'
    out = do(cmd, root)
    try:
        # in merge state we assume parent 1 is fine
        tag, dist = out.splitlines()[0].split()
        if tag == 'null':
            tag = '0.0'
            dist = int(dist) + 1
        return _hg_tagdist_normalize_tagcommit(root, tag, dist, node)
    except ValueError:
        pass  # unpacking failed, old hg


def archival_to_version(data):
    trace('data', data)
    if 'tag' in data:
        return meta(data['tag'])
    elif 'latesttag' in data:
        return meta(data['latesttag'],
                    distance=data['latesttagdistance'],
                    node=data['node'][:12])
    else:
        return meta('0.0', node=data.get('node', '')[:12])


def parse_archival(root):
    archival = os.path.join(root, '.hg_archival.txt')
    data = data_from_mime(archival)
    return archival_to_version(data)
