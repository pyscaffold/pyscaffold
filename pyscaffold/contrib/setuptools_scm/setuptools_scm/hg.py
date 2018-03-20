import os
from .utils import do, trace, data_from_mime, has_command
from .version import meta, tags_to_versions

FILES_COMMAND = 'hg locate -I .'


def _hg_tagdist_normalize_tagcommit(root, tag, dist, node):
    dirty = node.endswith('+')
    node = 'h' + node.strip('+')

    # Detect changes since the specified tag
    revset = ("(branch(.)"  # look for revisions in this branch only
              " and tag({tag!r})::."  # after the last tag
              # ignore commits that only modify .hgtags and nothing else:
              " and (merge() or file('re:^(?!\.hgtags).*$'))"
              " and not tag({tag!r}))"  # ignore the tagged commit itself
              ).format(tag=tag)
    if tag != '0.0':
        commits = do(['hg', 'log', '-r', revset, '--template', '{node|short}'],
                     root)
    else:
        commits = True
    trace('normalize', locals())
    if commits or dirty:
        return meta(tag, distance=dist, node=node, dirty=dirty)
    else:
        return meta(tag)


def parse(root):
    if not has_command('hg'):
        return
    identity_data = do('hg id -i -t', root).split()
    if not identity_data:
        return
    node = identity_data.pop(0)
    tags = tags_to_versions(identity_data)
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
        tags, dist = out.splitlines()[0].split()
        # pick latest tag from tag list
        tag = tags.split(':')[-1]
        if tag == 'null':
            tag = '0.0'
            dist = int(dist) + 1
        return _hg_tagdist_normalize_tagcommit(root, tag, dist, node)
    except ValueError:
        pass  # unpacking failed, old hg


def archival_to_version(data):
    trace('data', data)
    node = data.get('node', '')[:12]
    if node:
        node = 'h' + node
    if 'tag' in data:
        return meta(data['tag'])
    elif 'latesttag' in data:
        return meta(data['latesttag'],
                    distance=data['latesttagdistance'],
                    node=node)
    else:
        return meta('0.0', node=node)


def parse_archival(root):
    archival = os.path.join(root, '.hg_archival.txt')
    data = data_from_mime(archival)
    return archival_to_version(data)
