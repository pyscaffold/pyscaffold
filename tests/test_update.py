import logging
import os
import re
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace as Object

import pytest
from packaging.version import Version

from pyscaffold import __path__ as pyscaffold_paths
from pyscaffold import __version__, actions, info, update
from pyscaffold.file_system import chdir

from .helpers import in_ci, path_as_uri, skip_on_conda_build
from .system.helpers import normalize_run_args

EDITABLE_PYSCAFFOLD = re.compile(r"^-e.+pyscaffold.*$", re.M | re.I)


class VenvManager:
    def __init__(self, venv):
        self.installed = False
        self.venv = venv
        self.running_version = Version(__version__)
        self._orig_workdir = Path(".").resolve()

    def install(self, pkg=None, editable=False, **kwargs):
        target = [str(pkg)]
        if editable:
            target = ["--editable", *target]

        assert Path(self.venv.exe("python")).exists()
        assert str(self.venv.path) in str(self.venv.exe("python"))

        # Sometimes Windows complain about SSL, despite all the efforts on using a env
        # var for trusted hosts
        cmd = [
            *("pip", "install", *target),
            *("--trusted-host", "files.pythonhosted.org"),
            *("--trusted-host", "pypi.python.org"),
            *("--trusted-host", "files.pythonhosted.org"),
            *("--trusted-host", "pypi.org"),
        ]
        return self.run(*cmd, **kwargs)

    def _get_proj_dir(self) -> Path:
        if "TOXINIDIR" in os.environ:
            # so pytest runs within tox
            proj_dir = Path(os.environ["TOXINIDIR"])
            logging.debug("SRC via TOXINIDIR: %s", proj_dir)
        else:
            try:
                location = Path(pyscaffold_paths[0])
                assert location.parent.name == "src"
                proj_dir = location.parent.parent
            except:  # noqa
                print("\n\nInstall PyScaffold with python setup.py develop!\n\n")
                raise

            logging.debug("SRC via working_set: %s, location: %s", proj_dir, location)

        return proj_dir

    def _install_pre_built_wheel(self, proj_dir: Path):
        # CI should pre-build wheels that can be used.
        candidates = (proj_dir / "dist").glob("PyScaffold*.whl")
        wheel = next(iter(sorted(candidates, reverse=True, key=str)), None)
        assert wheel, "PyScaffold should be pre-built by CI, but it is not..."
        return self.install(path_as_uri(wheel))

    def _install_from_src(self, proj_dir: Path):
        env = {**os.environ, "SETUPTOOLS_SCM_PRETEND_VERSION": __version__}
        assert proj_dir.exists(), f"{proj_dir} is supposed to exist"
        out = self.install(proj_dir, editable=True, env=env)
        pkg_list = self.run("pip freeze")
        assert EDITABLE_PYSCAFFOLD.findall(pkg_list)
        return out

    def install_this_pyscaffold(self):
        # Normally the following command should do the trick
        # self.venv.install_package('PyScaffold')
        # but sadly pytest-virtualenv chokes on the src-layout of PyScaffold
        proj_dir = self._get_proj_dir()
        if in_ci():
            self._install_pre_built_wheel(proj_dir)
        else:
            self._install_from_src(proj_dir)

        # Make sure pyscaffold was not installed using PyPI
        assert self.running_version.public <= self.pyscaffold_version().public
        self.installed = True
        return self

    def install_pyscaffold(self, major, minor):
        ver = f"pyscaffold>={major}.{minor},<{major}.{minor + 1}a0"
        self.install(ver)
        installed_version = self.pyscaffold_version().release[:2]
        assert installed_version == (major, minor)
        self.installed = True
        return self

    def uninstall_pyscaffold(self):
        self.run("pip uninstall -y pyscaffold")
        putup = self.venv.exe("putup")
        assert str(self.venv.path.resolve()) not in str(Path(putup).resolve())
        self.installed = False
        return self

    def pyscaffold_version(self):
        try:
            cli_version = self.run("python -m pyscaffold.cli --version").lower()
            return Version(cli_version.replace("pyscaffold ", ""))
        except subprocess.CalledProcessError as ex:
            if (
                sys.version_info >= (3, 12)
                and "No module named 'pyscaffold.contrib.six.moves'" in ex.output
            ):
                pytest.skip("Cannot import from six.moves in Python >= 3.12")
            raise

    def putup(self, *args, **kwargs):
        args, kwargs = normalize_run_args(args, kwargs)
        print("putup", *args)
        print(self.venv.run("putup", *args, **kwargs))
        return self

    def run(self, *args, **kwargs):
        return self.venv.run(*args, **kwargs)


@pytest.fixture
def venv_mgr(venv):
    return VenvManager(venv)


@pytest.mark.slow
@pytest.mark.requires_src
@skip_on_conda_build
def test_update_version_3_0_to_3_1(tmp_path, with_coverage, venv_mgr):
    with chdir(str(tmp_path)):
        name = "my_old_project"
        project = tmp_path / "my_old_project"
        (
            venv_mgr.install_pyscaffold(3, 0)
            .putup(name)
            .uninstall_pyscaffold()
            .install_this_pyscaffold()
            .putup(f"--update {project}", with_coverage=with_coverage)
        )
    setup_cfg = Path(project, "setup.cfg").read_text(encoding="utf-8")
    assert "[options.entry_points]" in setup_cfg


@pytest.mark.slow
@pytest.mark.requires_src
@skip_on_conda_build
def test_update_version_3_0_to_3_1_pretend(tmp_path, with_coverage, venv_mgr):
    with chdir(str(tmp_path)):
        name = "my_old_project"
        project = tmp_path / "my_old_project"
        (
            venv_mgr.install_pyscaffold(3, 0)
            .putup(name)
            .uninstall_pyscaffold()
            .install_this_pyscaffold()
            .putup(f"--pretend --update {project}", with_coverage=with_coverage)
        )
    setup_cfg = Path(project, "setup.cfg").read_text(encoding="utf-8")
    assert "[options.entry_points]" not in setup_cfg


@pytest.mark.slow
@pytest.mark.requires_src
@skip_on_conda_build
def test_inplace_update(tmp_path, with_coverage, venv_mgr):
    # Given an existing project
    project = tmp_path / "my_old_project"
    cmd = f"--name my-ns-proj --package project --namespace my_ns {project}"
    venv_mgr.install_this_pyscaffold().putup(cmd)

    # With an existing configuration
    assert project / "setup.cfg"
    parser = ConfigParser()
    parser.read(project / "setup.cfg")
    assert parser["metadata"]["name"] == "my-ns-proj"
    assert parser["pyscaffold"]["package"] == "project"
    assert parser["pyscaffold"]["namespace"] == "my_ns"

    # And without some extensions
    for file in (".pre-commit-config.yaml", ".isort.cfg"):
        assert not Path(project, file).exists()

    # When the project is updated
    # without repeating the information already given
    # but adding some information/extensions
    with chdir(str(project)):
        venv_mgr.putup(
            "-vv --description asdf --pre-commit --update .",
            with_coverage=with_coverage,
        )

    # Then existing configuration should be preserved + the additions
    parser = ConfigParser()
    parser.read(project / "setup.cfg")
    assert parser["metadata"]["name"] == "my-ns-proj"
    assert parser["pyscaffold"]["package"] == "project"
    assert parser["pyscaffold"]["namespace"] == "my_ns"

    # Some information (metadata) require manual update
    # unless the --force option is used
    assert parser["metadata"]["description"] != "asdf"

    # New extensions should take effect
    for file in ("tox.ini", ".pre-commit-config.yaml", ".isort.cfg"):
        assert Path(project, file).exists()

    # While using the existing information
    parser = ConfigParser()
    parser.read(project / ".isort.cfg")
    assert parser["settings"]["known_first_party"] == "my_ns"


# ---- Slightly more isolated tests ----


def test_update_setup_cfg(tmpfolder):
    # Given an existing setup.cfg
    proj = Path(tmpfolder, "proj")
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "setup.cfg").write_text("[metadata]\n\n[pyscaffold]\n")
    # when we update it
    extensions = [Object(name="cirrus", persist=True), Object(name="no", persist=False)]
    opts = {"project_path": proj, "extensions": extensions}
    _, opts = actions.get_default_options({}, opts)
    update.update_setup_cfg({}, opts)
    cfg = info.read_setupcfg(proj / "setup.cfg")
    # then it should show the most update pyscaffold version
    assert cfg["pyscaffold"]["version"].value == __version__
    assert "cirrus" in cfg["pyscaffold"]["extensions"].value
    assert "no" not in cfg["pyscaffold"]["extensions"].value
    # and some configuration keys should be present
    assert "options" in cfg


def test_update_none_param(tmpfolder):
    invalid = """\
    [metadata]
    [pyscaffold]
    version = 4
    """
    Path(tmpfolder, "setup.cfg").write_text(dedent(invalid))
    extensions = [Object(name="x_foo_bar_x", persist=True)]
    _, opts = actions.get_default_options({}, {"extensions": extensions})
    opts["x_foo_bar_x_param"] = None
    # No parser exception should be found
    update.update_setup_cfg({}, opts)
    assert Path(tmpfolder, "setup.cfg").read_text()


def test_add_dependencies(tmpfolder):
    # Given an existing setup.cfg
    Path(tmpfolder, "setup.cfg").write_text("[options]\n")
    # when we update it
    opts = {"project_path": tmpfolder, "pretend": False}
    update.add_dependencies({}, opts)
    # then we should see the dependencies in install_requires
    cfg = info.read_setupcfg(Path(tmpfolder, "setup.cfg"))
    assert "install_requires" in str(cfg["options"])
    assert "importlib-metadata" in str(cfg["options"]["install_requires"])


def test_add_dependencies_with_comments(tmpfolder):
    # Given a setup.cfg with comments inside options (especially install_requires)
    config = """\
    [metadata]
    project_urls =
        Download = https://pypi.org/project/PyScaffold/#files
        # the previous line does not have a comment, it's just part of the URL
        Issues = https://github.com/pyscaffold/pyscaffold/issues  # this is a comment!
    [options]
    install_requires =
        importlib-metadata; python_version<"3.8"
        # Adding some comments here that are perfectly valid.
        some-other-dependency
        gitdep @ git+https://repo.com/gitdep@main#egg=gitdep
    packages = find_namespace:
    """
    Path(tmpfolder, "setup.cfg").write_text(dedent(config))
    # when we update it
    opts = {"project_path": tmpfolder, "pretend": False}
    update.add_dependencies({}, opts)
    # then the comments inside the options should still be there
    actual_setup_cfg = Path(tmpfolder, "setup.cfg").read_text()
    assert actual_setup_cfg == dedent(config)


@pytest.fixture
def existing_config(tmpfolder):
    config = """\
    [options]
    setup_requires =
        pyscaffold
        somedep>=3.8

    [pyscaffold]
    version = 3.2.2
    """
    cfg = Path(tmpfolder) / "setup.cfg"
    cfg.write_text(dedent(config))

    yield cfg


def test_handover_setup_requires(tmpfolder, existing_config):
    # Given an existing setup.cfg with setup_requires
    # when we update it
    opts = {"project_path": tmpfolder, "pretend": False}
    update.handover_setup_requires({}, opts)
    cfg = info.read_setupcfg(existing_config)
    # then setup_requirements should not be included
    assert "setup_requires" not in str(cfg["options"])


def test_handover_setup_requires_no_pyproject(tmpfolder, existing_config):
    # Given an existing setup.cfg with outdated setup_requires and pyscaffold version,
    # when we update it without no_pyproject
    opts = {"project_path": tmpfolder, "pretend": False, "isolated_build": False}
    update.handover_setup_requires({}, opts)
    cfg = info.read_setupcfg(existing_config)
    # then setup_requirements is left alone
    assert cfg["options"]["setup_requires"]


@pytest.fixture
def pyproject_from_old_extension(tmpfolder):
    """Old pyproject.toml file as produced by pyscaffoldext-pyproject"""
    config = """\
    [build-system]
    requires = ["setuptools"]
    """
    pyproject = Path(tmpfolder) / "pyproject.toml"
    pyproject.write_text(dedent(config))
    yield pyproject


def test_update_pyproject_toml(tmpfolder, pyproject_from_old_extension):
    update.update_pyproject_toml({}, {"project_path": tmpfolder, "pretend": False})
    pyproject = info.read_pyproject(pyproject_from_old_extension)
    deps = " ".join(pyproject["build-system"]["requires"])
    assert "setuptools_scm" in deps
    assert "setuptools.build_meta" in pyproject["build-system"]["build-backend"]
    assert "setuptools_scm" in pyproject["tool"]


def test_migrate_setup_requires(tmpfolder, existing_config):
    # When a project with setup.cfg :: setup_requires is updated
    opts = {"project_path": tmpfolder, "pretend": False}
    _, opts = update.handover_setup_requires({}, opts)
    update.update_pyproject_toml({}, opts)
    # then the minimal dependencies are added
    pyproject = info.read_pyproject(tmpfolder)
    deps = " ".join(pyproject["build-system"]["requires"])
    assert "setuptools_scm" in deps
    # old dependencies are migrated from setup.cfg
    assert "somedep>=3.8" in deps
    setupcfg = info.read_setupcfg(existing_config)
    assert "setup_requires" not in setupcfg["options"]
    # but pyscaffold is not included.
    assert "pyscaffold" not in deps


def test_replace_find_with_find_namespace(tmpfolder):
    # Given an old setup.cfg based on packages find:
    config = """\
    [options]
    zip_safe = False
    packages = find:

    [options.packages.find]
    where = src
    exclude =
        tests
    """
    Path(tmpfolder, "setup.cfg").write_text(dedent(config))
    # when we update it
    opts = {"project_path": tmpfolder, "pretend": False}
    update.replace_find_with_find_namespace({}, opts)
    # then we should see find_namespace instead
    cfg = info.read_setupcfg(Path(tmpfolder, "setup.cfg"))
    assert cfg["options"]["packages"].value == "find_namespace:"
    assert "options.packages.find" in cfg
    assert cfg["options.packages.find"]["where"].value == "src"
    assert cfg["options.packages.find"]["exclude"].value.strip() == "tests"
