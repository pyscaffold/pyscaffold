import os
import sys
from os import environ
from os.path import exists, isdir
from os.path import join as path_join
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from pyscaffold.file_system import chdir

from .helpers import run, run_common_tasks

pytestmark = [pytest.mark.slow, pytest.mark.system]


def is_venv():
    """Check if the tests are running inside a venv"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


@pytest.fixture(autouse=True)
def cwd(tmpdir):
    """Guarantee a blank folder as workspace"""
    with tmpdir.as_cwd():
        yield tmpdir


def test_ensure_inside_test_venv(putup):
    # This is a METATEST
    # Here we ensure `putup` is installed inside tox so we know we are testing the
    # correct version of pyscaffold and not one the devs installed to use in other
    # projects
    assert ".tox" in putup


BUILD_DEPS = ["wheel", "setuptools_scm"]


def test_putup(cwd, putup):
    # Given pyscaffold is installed,
    # when we run putup
    run(f"{putup} myproj")
    # then no error should be raised when running the common tasks
    with cwd.join("myproj").as_cwd():
        # then the new version of PyScaffold should produce packages with
        # the correct build deps
        for dep in BUILD_DEPS:
            assert dep + ">=" in Path("setup.cfg").read_text()
        # and no error should be raised when running the common tasks
        run_common_tasks()


def test_putup_with_update(cwd, putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} myproj")
    # when we run putup with the update flag
    run(f"{putup} --update myproj")
    # then no difference should be found
    with cwd.join("myproj").as_cwd():
        git_diff = run("git diff")
        assert git_diff.strip() == ""


def test_putup_with_update_dirty_workspace(cwd, putup):
    run(f"{putup} myproj")
    with chdir("myproj"):
        with open("setup.py", "w") as fh:
            fh.write("DIRTY")
    with pytest.raises(CalledProcessError):
        run(f"{putup} --update myproj")
    run(f"{putup} --update myproj --force")


def test_differing_package_name(cwd, putup):
    # Given pyscaffold is installed,
    # when we run putup
    run(f"{putup} my-cool-proj -p myproj")
    # then the folder structure should respect the names
    assert isdir("my-cool-proj")
    assert isdir("my-cool-proj/src/myproj")
    # then no error should be raised when running the common tasks
    with cwd.join("my-cool-proj").as_cwd():
        run_common_tasks()


def test_update(putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} myproj")
    assert not exists("myproj/tox.ini")
    # when it is updated
    run(f"{putup} --update --travis myproj")
    # then complementary files should be created
    assert exists("myproj/.travis.yml")


def test_force(cwd, putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} myproj")
    assert not exists("myproj/tox.ini")
    # when it is forcefully updated
    run(f"{putup} --force --tox myproj")
    # then complementary files should be created
    assert exists("myproj/tox.ini")
    if environ.get("DISTRIB") == "ubuntu":
        # and added features should work properly
        with cwd.join("myproj").as_cwd():
            run("tox -e py")


# -- Extensions --


def test_tox_docs(cwd, tox, putup):
    # Given pyscaffold project is created with --tox
    run(f"{putup} myproj --tox")
    with cwd.join("myproj").as_cwd():
        # when we can call tox -e docs
        run(f"{tox} -e docs")
        # then documentation will be generated.
        assert exists("docs/api/modules.rst")
        assert exists("docs/_build/html/index.html")


def test_tox_doctests(cwd, tox, putup):
    # Given pyscaffold project is created with --tox
    run(f"{putup} myproj --tox")
    with cwd.join("myproj").as_cwd():
        # when we can call tox
        run(f"{tox} -e doctests")
        # then tests will execute


def test_tox_tests(cwd, tox, putup):
    # Given pyscaffold project is created with --tox
    run(f"{putup} myproj --tox")
    with cwd.join("myproj").as_cwd():
        # when we can call tox
        run(tox)
        # then tests will execute


@pytest.mark.parametrize(
    "extension, kwargs, filename",
    (
        ("pre-commit", {}, ".pre-commit-config.yaml"),
        ("travis", {}, ".travis.yml"),
        ("gitlab", {}, ".gitlab-ci.yml"),
    ),
)
def test_extensions(cwd, putup, extension, kwargs, filename):
    # Given pyscaffold is installed,
    # when we call putup with extensions
    name = "myproj-" + extension
    run(f"{putup} -vv --{extension} {name}")
    with cwd.join(name).as_cwd():
        # then special files should be created
        assert exists(filename)
        # and all the common tasks should run properly
        run_common_tasks(**kwargs)


def test_no_skeleton(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --no-skeleton
    run(f"{putup} myproj --no-skeleton")
    with cwd.join("myproj").as_cwd():
        # then no skeleton file should be created
        assert not exists("src/myproj/skeleton.py")
        assert not exists("tests/test_skeleton.py")
        # and all the common tasks should run properly
        run_common_tasks(tests=False)


def test_namespace(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --namespace
    run(f"{putup} nested_project -p my_package --namespace com.blue_yonder")
    # then a very complicated module hierarchy should exist
    path = "nested_project/src/com/blue_yonder/my_package/skeleton.py"
    assert exists(path)
    assert not exists("nested_project/src/my_package")
    with cwd.join("nested_project").as_cwd():
        run_common_tasks()
    # and pyscaffold should remember the options during an update
    run(f"{putup} nested_project --update -vv")
    assert exists(path)
    assert not exists("nested_project/src/nested_project")
    assert not exists("nested_project/src/my_package")


def test_namespace_no_skeleton(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --namespace and --no-skeleton
    run(
        f"{putup} nested_project --no-skeleton "
        "-p my_package --namespace com.blue_yonder"
    )
    # then a very complicated module hierarchy should exist
    path = "nested_project/src/com/blue_yonder/my_package"
    assert isdir(path)
    # but no skeleton.py
    assert not exists(path_join(path, "skeleton.py"))


def test_new_project_does_not_fail_pre_commit(cwd, pre_commit, putup):
    # Given pyscaffold is installed,
    # when we call putup with extensions and pre-commit
    name = "my_project"
    run(
        f"{putup} --pre-commit --travis --gitlab --tox "
        "-p my_package --namespace com.blue_yonder " + name
    )
    with cwd.join(name).as_cwd():
        # then the newly generated files should not result in errors when
        # pre-commit runs...
        try:
            run(f"{pre_commit} install")
            run(f"{pre_commit} run --all")
        except CalledProcessError as ex:
            if os.name == "nt" and (
                "filename or extension is too long"
                in ((ex.stdout or "") + (ex.stderr or ""))
            ):
                pytest.skip("Sometimes Windows have problems with nested files")
                # Even if we try to change that by configuring the CI
                # environment
            else:
                raise
