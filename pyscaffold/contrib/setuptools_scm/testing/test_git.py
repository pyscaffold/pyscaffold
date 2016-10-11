from setuptools_scm import integration
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
    assert wd.version == '0.0'

    wd.commit_testfile()
    assert wd.version.startswith('0.1.dev1+')
    assert not wd.version.endswith('1-')

    wd('git tag v0.1')
    assert wd.version == '0.1'

    wd.write('test.txt', 'test2')
    assert wd.version.startswith('0.2.dev0+')

    wd.commit_testfile()
    assert wd.version.startswith('0.2.dev1+')

    wd('git tag version-0.2')
    assert wd.version.startswith('0.2')


@pytest.mark.issue(86)
def test_git_dirty_notag(wd):
    wd.commit_testfile()
    wd.write('test.txt', 'test2')
    wd("git add test.txt")
    assert wd.version.startswith('0.1.dev1')
    today = date.today()
    # we are dirty, check for the tag
    assert today.strftime('.d%Y%m%d') in wd.version


def test_find_files_stop_at_root_git(wd):
    wd.commit_testfile()
    wd.cwd.ensure('project/setup.cfg')
    assert integration.find_files(str(wd.cwd/'project')) == []


def test_alphanumeric_tags_match(wd):
    wd.commit_testfile()
    wd('git tag newstyle-development-started')
    assert wd.version.startswith('0.1.dev1+')
