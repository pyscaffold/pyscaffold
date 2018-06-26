# -*- coding: utf-8 -*-
from os import environ
from os.path import exists, isdir

import pytest

from .helpers import run

pytestmark = [pytest.mark.slow, pytest.mark.system]


def run_common_tasks(tests=True, flake8=True):
    if tests:
        run('python setup.py test')

    run('python setup.py doctest')
    run('python setup.py docs')
    run('python setup.py --version')
    run('python setup.py sdist')
    run('python setup.py bdist')

    if flake8 and environ.get('coverage') == 'true':
        run('flake8 --count')


def test_putup(tmpdir):
    # Given pyscaffold is installed,
    # when we run putup
    with tmpdir.as_cwd():
        run('putup myproj')
    # then no error should be raised when running the common tasks
    with tmpdir.join('myproj').as_cwd():
        run_common_tasks()


def test_putup_with_update(tmpdir):
    # Given pyscaffold is installed,
    # and a project already created
    with tmpdir.as_cwd():
        run('putup myproj')
        # when we run putup with the update flag
        run('putup --update myproj')
    # then no difference should be found
    with tmpdir.join('myproj').as_cwd():
        git_diff = run('git diff')
        assert git_diff.strip() == ''


def test_differing_package_name(tmpdir):
    # Given pyscaffold is installed,
    # when we run putup
    with tmpdir.as_cwd():
        run('putup my-cool-proj -p myproj')
        # then the folder structure should respect the names
        assert isdir('my-cool-proj')
        assert isdir('my-cool-proj/src/myproj')
    # then no error should be raised when running the common tasks
    with tmpdir.join('my-cool-proj').as_cwd():
        run_common_tasks()


def test_force_overwrite(tmpdir):
    # Given pyscaffold is installed,
    # and a project already created
    with tmpdir.as_cwd():
        run('putup myproj')
        assert not exists('myproj/tox.ini')
        # when it is forcefully updated
        run('putup --force --tox myproj')
        # then complementary files should be created
        assert exists('myproj/tox.ini')
    if environ.get('DISTRIB') == 'ubuntu':
        # and added features should work properly
        with tmpdir.join('myproj').as_cwd():
            run('tox -e py')


@pytest.mark.parametrize('extension, kwargs, filename', (
    ('pre-commit', {}, '.pre-commit-config.yaml'),
    ('travis', {}, '.travis.yml'),
    ('gitlab', {}, '.gitlab-ci.yml'),
    ('django', {'flake8': False}, 'manage.py'),
))
def test_extensions(tmpdir, extension, kwargs, filename):
    # Given pyscaffold is installed,
    with tmpdir.as_cwd():
        # when we call putup with extensions
        name = 'myproj' + extension
        run('putup', '--'+extension, name)
        with tmpdir.join(name).as_cwd():
            # then special files should be created
            assert exists(filename)
            # and all the common tasks should run properly
            run_common_tasks(**kwargs)


def test_no_skeleton(tmpdir):
    # Given pyscaffold is installed,
    with tmpdir.as_cwd():
        # when we call putup with --no-skeleton
        run('putup myproj --no-skeleton')
        with tmpdir.join('myproj').as_cwd():
            # then no skeleton file should be created
            assert not exists('src/myproj/skeleton.py')
            assert not exists('tests/test_skeleton.py')
            # and all the common tasks should run properly
            run_common_tasks(tests=False)
