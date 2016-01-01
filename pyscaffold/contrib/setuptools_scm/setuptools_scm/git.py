from .utils import do, do_ex, trace
from .version import meta
from os.path import abspath, realpath


FILES_COMMAND = 'git ls-files'
DEFAULT_DESCRIBE = 'git describe --dirty --tags --long --match *.*'


def parse(root, describe_command=DEFAULT_DESCRIBE):
    real_root, _, ret = do_ex('git rev-parse --show-toplevel', root)
    if ret:
        return
    trace('real root', real_root)
    if abspath(realpath(real_root)) != abspath(realpath(root)):
        return
    rev_node, _, ret = do_ex('git rev-parse --verify --quiet HEAD', root)
    if ret:
        return meta('0.0')
    rev_node = rev_node[:7]
    out, err, ret = do_ex(describe_command, root)
    if '-' not in out and '.' not in out:
        revs = do('git rev-list HEAD', root)
        count = revs.count('\n')
        if ret:
            out = rev_node
        return meta('0.0', distance=count + 1, node=out)
    if ret:
        return
    dirty = out.endswith('-dirty')
    if dirty:
        out = out.rsplit('-', 1)[0]

    tag, number, node = out.rsplit('-', 2)
    number = int(number)
    if number:
        return meta(tag, distance=number, node=node, dirty=dirty)
    else:
        return meta(tag, dirty=dirty, node=node)
