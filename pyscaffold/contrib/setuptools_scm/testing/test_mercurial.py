from setuptools_scm import format_version
from setuptools_scm.hg import archival_to_version, parse
from setuptools_scm import integration

import pytest


@pytest.fixture
def wd(wd):
    wd('hg init')
    wd.add_command = 'hg add .'
    wd.commit_command = 'hg commit -m test-{reason} -u test -d "0 0"'
    return wd


archival_mapping = {
    '1.0': {'tag': '1.0'},
    '1.1.dev3+h000000000000': {
        'latesttag': '1.0',
        'latesttagdistance': '3',
        'node': '0'*20,
    },
    '0.0': {
        'node': '0'*20,
    },
    '1.2.2': {'tag': 'release-1.2.2'},
    '1.2.2.dev0': {'tag': 'release-1.2.2.dev'},

}


@pytest.mark.parametrize('expected,data', sorted(archival_mapping.items()))
def test_archival_to_version(expected, data):
    version = archival_to_version(data)
    assert format_version(
        version,
        version_scheme='guess-next-dev',
        local_scheme='node-and-date') == expected


def test_find_files_stop_at_root_hg(wd):
    wd.commit_testfile()
    wd.cwd.ensure('project/setup.cfg')
    assert integration.find_files(str(wd.cwd/'project')) == []


# XXX: better tests for tag prefixes
def test_version_from_hg_id(wd):
    assert wd.version == '0.0'

    wd.commit_testfile()
    assert wd.version.startswith('0.1.dev2+')

    # tagging commit is considered the tag
    wd('hg tag v0.1 -u test -d "0 0"')
    assert wd.version == '0.1'

    wd.commit_testfile()
    assert wd.version.startswith('0.2.dev2')

    wd('hg up v0.1')
    assert wd.version == '0.1'

    # commit originating from the taged revision
    # that is not a actual tag
    wd.commit_testfile()
    assert wd.version.startswith('0.2.dev1+')

    # several tags
    wd('hg up')
    wd('hg tag v0.2 -u test -d "0 0"')
    wd('hg tag v0.3 -u test -d "0 0" -r v0.2')
    assert wd.version == '0.3'


def test_version_from_archival(wd):
    # entrypoints are unordered,
    # cleaning the wd ensure this test wont break randomly
    wd.cwd.join('.hg').remove()
    wd.write(
        '.hg_archival.txt',
        'node: 000000000000\n'
        'tag: 0.1\n'
    )
    assert wd.version == '0.1'

    wd.write(
        '.hg_archival.txt',
        'node: 000000000000\n'
        'latesttag: 0.1\n'
        'latesttagdistance: 3\n'
    )

    assert wd.version == '0.2.dev3+h000000000000'


@pytest.mark.issue('#72')
def test_version_in_merge(wd):
    wd.commit_testfile()
    wd.commit_testfile()
    wd('hg up 0')
    wd.commit_testfile()
    wd('hg merge --tool :merge')
    assert wd.version is not None


@pytest.mark.issue(128)
def test_parse_no_worktree(tmpdir):
    ret = parse(str(tmpdir))
    assert ret is None


@pytest.fixture
def version_1_0(wd):
    wd('hg branch default')
    wd.commit_testfile()
    wd('hg tag 1.0 -u test -d "0 0"')
    return wd


@pytest.fixture
def pre_merge_commit_after_tag(wd, version_1_0):
    wd('hg branch testbranch')
    wd.write('branchfile', 'branchtext')
    wd(wd.add_command)
    wd.commit()
    wd('hg update default')
    wd('hg merge testbranch')
    return wd


@pytest.mark.usefixtures("pre_merge_commit_after_tag")
def test_version_bump_before_merge_commit(wd):
    assert wd.version.startswith('1.1.dev1+')


@pytest.mark.issue(219)
@pytest.mark.usefixtures("pre_merge_commit_after_tag")
def test_version_bump_from_merge_commit(wd):
    wd.commit()
    assert wd.version.startswith('1.1.dev3+')  # issue 219


@pytest.mark.usefixtures("version_1_0")
def test_version_bump_from_commit_including_hgtag_mods(wd):
    """ Test the case where a commit includes changes to .hgtags and other files
    """
    with wd.cwd.join('.hgtags').open('a') as tagfile:
        tagfile.write('0  0\n')
    wd.write('branchfile', 'branchtext')
    wd(wd.add_command)
    assert wd.version.startswith('1.1.dev1+')  # bump from dirty version
    wd.commit()  # commits both the testfile _and_ .hgtags
    assert wd.version.startswith('1.1.dev2+')
