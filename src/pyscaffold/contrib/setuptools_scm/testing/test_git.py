from setuptools_scm import integration
from setuptools_scm.utils import do
from setuptools_scm import git
import pytest
from datetime import date


@pytest.fixture
def wd(wd):
    wd('git init')
    wd('git config user.email test@example.com')
    wd('git config user.name "a test"')
    wd.add_command = 'git add .'
    wd.commit_command = 'git commit -m test-{reason}'
    return wd


def test_version_from_git(wd):
    assert wd.version == '0.1.dev0'

    wd.commit_testfile()
    assert wd.version.startswith('0.1.dev1+g')
    assert not wd.version.endswith('1-')

    wd('git tag v0.1')
    assert wd.version == '0.1'

    wd.write('test.txt', 'test2')
    assert wd.version.startswith('0.2.dev0+g')

    wd.commit_testfile()
    assert wd.version.startswith('0.2.dev1+g')

    wd('git tag version-0.2')
    assert wd.version.startswith('0.2')

    wd.commit_testfile()
    wd('git tag version-0.2.post210+gbe48adfpost3+g0cc25f2')
    assert wd.version.startswith('0.2')


@pytest.mark.issue(108)
@pytest.mark.issue(109)
def test_git_worktree(wd):
    wd.write('test.txt', 'test2')
    # untracked files dont change the state
    assert wd.version == '0.1.dev0'
    wd('git add test.txt')
    assert wd.version.startswith('0.1.dev0+d')


@pytest.mark.issue(86)
def test_git_dirty_notag(wd):
    wd.commit_testfile()
    wd.write('test.txt', 'test2')
    wd("git add test.txt")
    assert wd.version.startswith('0.1.dev1')
    today = date.today()
    # we are dirty, check for the tag
    assert today.strftime('.d%Y%m%d') in wd.version


@pytest.fixture
def shallow_wd(wd, tmpdir):
    wd.commit_testfile()
    wd.commit_testfile()
    wd.commit_testfile()
    target = tmpdir.join('wd_shallow')
    do(['git', 'clone', "file://%s" % wd.cwd, str(target,), '--depth=1'])
    return target


def test_git_parse_shallow_warns(shallow_wd, recwarn):
    git.parse(str(shallow_wd))
    msg = recwarn.pop()
    assert 'is shallow and may cause errors' in str(msg.message)


def test_git_parse_shallow_fail(shallow_wd):
    with pytest.raises(ValueError) as einfo:
        git.parse(str(shallow_wd), pre_parse=git.fail_on_shallow)

    assert 'git fetch' in str(einfo.value)


def test_git_shallow_autocorrect(shallow_wd, recwarn):
    git.parse(str(shallow_wd), pre_parse=git.fetch_on_shallow)
    msg = recwarn.pop()
    assert 'git fetch was used to rectify' in str(msg.message)
    git.parse(str(shallow_wd), pre_parse=git.fail_on_shallow)


def test_find_files_stop_at_root_git(wd):
    wd.commit_testfile()
    wd.cwd.ensure('project/setup.cfg')
    assert integration.find_files(str(wd.cwd/'project')) == []


@pytest.mark.issue(128)
def test_parse_no_worktree(tmpdir):
    ret = git.parse(str(tmpdir))
    assert ret is None


def test_alphanumeric_tags_match(wd):
    wd.commit_testfile()
    wd('git tag newstyle-development-started')
    assert wd.version.startswith('0.1.dev1+g')
