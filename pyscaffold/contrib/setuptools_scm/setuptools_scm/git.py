from .utils import do_ex, trace
from .version import meta
from os.path import abspath, normcase, realpath


FILES_COMMAND = 'git ls-files'
DEFAULT_DESCRIBE = 'git describe --tags --long --match *.*'


def _normalized(path):
    return normcase(abspath(realpath(path)))


class GitWorkdir(object):
    def __init__(self, path):
        self.path = path

    def do_ex(self, cmd):
        return do_ex(cmd, cwd=self.path)

    @classmethod
    def from_potential_worktree(cls, wd):
        real_wd, _, ret = do_ex('git rev-parse --show-toplevel', wd)
        if ret:
            return
        trace('real root', real_wd)
        if _normalized(real_wd) != _normalized(wd):
            return

        return cls(real_wd)

    def is_dirty(self):
        out, _, _ = self.do_ex("git status --porcelain")
        return bool(out)

    def node(self):
        rev_node, _, ret = self.do_ex('git rev-parse --verify --quiet HEAD')
        if not ret:
            return rev_node[:7]

    def count_all_nodes(self):
        revs, _, _ = self.do_ex('git rev-list HEAD')
        return revs.count('\n') + 1


def parse(root, describe_command=DEFAULT_DESCRIBE):
    wd = GitWorkdir(root)

    rev_node = wd.node()
    dirty = wd.is_dirty()

    if rev_node is None:
        return meta('0.0', dirty=dirty)

    out, err, ret = do_ex(describe_command, root)
    if ret:
        return meta(
            '0.0',
            distance=wd.count_all_nodes(),
            node=rev_node,
            dirty=dirty,
        )

    tag, number, node = out.rsplit('-', 2)
    number = int(number)
    if number:
        return meta(tag, distance=number, node=node, dirty=dirty)
    else:
        return meta(tag, node=node, dirty=dirty)
