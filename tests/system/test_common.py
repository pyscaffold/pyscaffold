import os
import sys
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from pyscaffold.file_system import chdir
from pyscaffold.info import read_pyproject

from ..helpers import skip_on_conda_build
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


@skip_on_conda_build
@pytest.mark.requires_src
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
        pyproject_toml = read_pyproject(".")
        stored_deps = " ".join(pyproject_toml["build-system"]["requires"])
        for dep in BUILD_DEPS:
            assert dep in stored_deps
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


def test_putup_with_update_and_namespace(cwd, putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} --namespace myns --package myproj myns-myproj")
    # when we run putup with the update flag
    run(f"{putup} --update myns-myproj")
    # then no difference should be found
    with cwd.join("myns-myproj").as_cwd():
        git_diff = run("git diff")
        assert git_diff.strip() == ""


def test_differing_package_name(cwd, putup):
    # Given pyscaffold is installed,
    # when we run putup
    run(f"{putup} my-cool-proj -p myproj")
    # then the folder structure should respect the names
    assert Path("my-cool-proj").is_dir()
    assert Path("my-cool-proj/src/myproj").is_dir()
    # then no error should be raised when running the common tasks
    with cwd.join("my-cool-proj").as_cwd():
        run_common_tasks()


def test_update(putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} myproj")
    assert not Path("myproj/.cirrus.yml").exists()
    # when it is updated
    run(f"{putup} --update --cirrus myproj")
    # then complementary files should be created
    assert Path("myproj/.cirrus.yml").exists()


def test_force(cwd, putup):
    # Given pyscaffold is installed,
    # and a project already created
    run(f"{putup} myproj")
    assert not Path("myproj/.cirrus.yml").exists()
    # when it is forcefully updated
    run(f"{putup} --force --cirrus myproj")
    # then complementary files should be created
    assert Path("myproj/.cirrus.yml").exists()


# -- Extensions --


def test_tox_docs(cwd, tox, putup):
    # Given pyscaffold project is created
    run(f"{putup} myproj")
    with cwd.join("myproj").as_cwd():
        # when we can call tox -e docs
        run(f"{tox} -e docs")
        # then documentation will be generated.
        assert Path("docs/api/modules.rst").exists()
        assert Path("docs/_build/html/index.html").exists()


def test_tox_doctests(cwd, tox, putup):
    # Given pyscaffold project is created
    run(f"{putup} myproj")
    with cwd.join("myproj").as_cwd():
        # when we can call tox
        run(f"{tox} -e doctests")
        # then tests will execute


def test_tox_tests(cwd, tox, putup):
    # Given pyscaffold project is created
    run(f"{putup} myproj")
    with cwd.join("myproj").as_cwd():
        # when we can call tox
        run(tox)
        # then tests will execute


def test_tox_build(cwd, tox, putup):
    # Given pyscaffold project is created
    run(f"{putup} myproj")
    with cwd.join("myproj").as_cwd():
        # when we can call tox
        # then tasks will execute
        run(f"{tox} -e build")
        # and a pure Python distribution is created
        assert len(list(Path("dist").glob("*py3-none-any.whl"))) > 0
        try:
            run(f"{tox} -e clean")
            assert not Path("dist").exists()
            assert not Path("build").exists()
        except CalledProcessError as ex:
            msg = (ex.stdout or "") + (ex.stderr or "")
            if os.name == "nt" and ("unicodeescape" in msg):
                pytest.skip("Sometimes Windows have problems with rmtree")


@pytest.mark.parametrize(
    "extension, kwargs, filename",
    (
        ("pre-commit", {}, ".pre-commit-config.yaml"),
        ("cirrus", {}, ".cirrus.yml"),
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
        assert Path(filename).exists()
        # and all the common tasks should run properly
        run_common_tasks(**kwargs)


def test_no_skeleton(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --no-skeleton
    run(f"{putup} myproj --no-skeleton")
    with cwd.join("myproj").as_cwd():
        # then no skeleton file should be created
        assert not Path("src/myproj/skeleton.py").exists()
        assert not Path("tests/test_skeleton.py").exists()
        # and all the common tasks should run properly
        run_common_tasks(tests=False)


def test_namespace(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --namespace
    run(f"{putup} nested_project -p my_package --namespace com.blue_yonder")
    # then a very complicated module hierarchy should exist
    path = "nested_project/src/com/blue_yonder/my_package/skeleton.py"
    assert Path(path).exists()
    assert not Path("nested_project/src/my_package").exists()
    with cwd.join("nested_project").as_cwd():
        run_common_tasks()
        # sphinx should be able to document modules that use PEP 420
        assert Path("docs/api/com.blue_yonder.my_package.rst").exists()
    # and pyscaffold should remember the options during an update
    run(f"{putup} nested_project --update -vv")
    assert Path(path).exists()
    assert not Path("nested_project/src/nested_project").exists()
    assert not Path("nested_project/src/my_package").exists()


def test_namespace_no_skeleton(cwd, putup):
    # Given pyscaffold is installed,
    # when we call putup with --namespace and --no-skeleton
    run(
        f"{putup} nested_project --no-skeleton "
        "-p my_package --namespace com.blue_yonder"
    )
    # then a very complicated module hierarchy should exist
    path = Path("nested_project/src/com/blue_yonder/my_package")
    assert path.is_dir()
    # but no skeleton.py
    assert not (path / "skeleton.py").exists()


def test_new_project_does_not_fail_pre_commit(cwd, pre_commit, putup):
    # Given pyscaffold is installed,
    # when we call putup with extensions and pre-commit
    name = "my_project"
    run(
        f"{putup} --pre-commit --cirrus --gitlab "
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
