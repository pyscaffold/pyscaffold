# -*- coding: utf-8 -*-
import sys
from os import environ
from os.path import exists, isdir
from os.path import join as path_join
from subprocess import CalledProcessError

import pytest

from pyscaffold.utils import chdir

from .helpers import run, run_common_tasks

pytestmark = [pytest.mark.slow, pytest.mark.system]

COOKIECUTTER = 'https://github.com/FlorianWilhelm/cookiecutter-pypackage.git'


def is_venv():
    """Check if the tests are running inside a venv"""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


@pytest.fixture(autouse=True)
def cwd(tmpdir):
    """Guarantee a blank folder as workspace"""
    with tmpdir.as_cwd():
        yield tmpdir


def test_ensure_inside_test_venv():
    # This is a METATEST
    # Here we ensure `putup` is installed inside tox or
    # a local virtualenv (pytest-runner), so we know we are testing the correct
    # version of pyscaffold and not one the devs installed to use in other
    # projects
    assert '.tox' in run('which putup') or is_venv()


def test_putup(cwd):
    # Given pyscaffold is installed,
    # when we run putup
    run('putup myproj')
    # then no error should be raised when running the common tasks
    with cwd.join('myproj').as_cwd():
        run_common_tasks()


def test_putup_with_update(cwd):
    # Given pyscaffold is installed,
    # and a project already created
    run('putup myproj')
    # when we run putup with the update flag
    run('putup --update myproj')
    # then no difference should be found
    with cwd.join('myproj').as_cwd():
        git_diff = run('git diff')
        assert git_diff.strip() == ''


def test_putup_with_update_dirty_workspace(cwd):
    run('putup myproj')
    with chdir('myproj'):
        with open('setup.py', 'w') as fh:
            fh.write('DIRTY')
    with pytest.raises(CalledProcessError):
        run('putup --update myproj')
    run('putup --update myproj --force')


def test_differing_package_name(cwd):
    # Given pyscaffold is installed,
    # when we run putup
    run('putup my-cool-proj -p myproj')
    # then the folder structure should respect the names
    assert isdir('my-cool-proj')
    assert isdir('my-cool-proj/src/myproj')
    # then no error should be raised when running the common tasks
    with cwd.join('my-cool-proj').as_cwd():
        run_common_tasks()


def test_update():
    # Given pyscaffold is installed,
    # and a project already created
    run('putup myproj')
    assert not exists('myproj/tox.ini')
    # when it is updated
    run('putup --update --travis myproj')
    # then complementary files should be created
    assert exists('myproj/.travis.yml')


def test_force(cwd):
    # Given pyscaffold is installed,
    # and a project already created
    run('putup myproj')
    assert not exists('myproj/tox.ini')
    # when it is forcefully updated
    run('putup --force --tox myproj')
    # then complementary files should be created
    assert exists('myproj/tox.ini')
    if environ.get('DISTRIB') == 'ubuntu':
        # and added features should work properly
        with cwd.join('myproj').as_cwd():
            run('tox -e py')


# -- Extensions --

@pytest.mark.parametrize('extension, kwargs, filename', (
    ('pre-commit', {}, '.pre-commit-config.yaml'),
    ('travis', {}, '.travis.yml'),
    ('gitlab', {}, '.gitlab-ci.yml'),
    ('django', {'flake8': False}, 'manage.py'),
))
def test_extensions(cwd, extension, kwargs, filename):
    # Given pyscaffold is installed,
    # when we call putup with extensions
    name = 'myproj' + extension
    run('putup', '--'+extension, name)
    with cwd.join(name).as_cwd():
        # then special files should be created
        assert exists(filename)
        # and all the common tasks should run properly
        run_common_tasks(**kwargs)


def test_no_skeleton(cwd):
    # Given pyscaffold is installed,
    # when we call putup with --no-skeleton
    run('putup myproj --no-skeleton')
    with cwd.join('myproj').as_cwd():
        # then no skeleton file should be created
        assert not exists('src/myproj/skeleton.py')
        assert not exists('tests/test_skeleton.py')
        # and all the common tasks should run properly
        run_common_tasks(tests=False)


def test_namespace(cwd):
    # Given pyscaffold is installed,
    # when we call putup with --namespace
    run('putup nested_project -p my_package --namespace com.blue_yonder')
    # then a very complicated module hierarchy should exist
    path = 'nested_project/src/com/blue_yonder/my_package/skeleton.py'
    assert exists(path)
    with cwd.join('nested_project').as_cwd():
        run_common_tasks()
    # and pyscaffold should remember the options during an update
    run('putup nested_project --update')
    assert exists(path)
    assert not exists('nested_project/src/nested_project')
    assert not exists('nested_project/src/my_package')


def test_namespace_no_skeleton(cwd):
    # Given pyscaffold is installed,
    # when we call putup with --namespace and --no-skeleton
    run('putup nested_project --no-skeleton '
        '-p my_package --namespace com.blue_yonder')
    # then a very complicated module hierarchy should exist
    path = 'nested_project/src/com/blue_yonder/my_package'
    assert isdir(path)
    # but no skeleton.py
    assert not exists(path_join(path, 'skeleton.py'))


def test_namespace_cookiecutter(cwd):
    # Given pyscaffold is installed,
    # when we call putup with --namespace and --cookiecutter
    run('putup myproj --namespace nested.ns --cookiecutter ' + COOKIECUTTER)
    # then a very complicated module hierarchy should exist
    assert isdir('myproj/src/nested/ns/myproj')
    # and all the common tasks should run properly
    with cwd.join('myproj').as_cwd():
        run_common_tasks(flake8=False, tests=False)
