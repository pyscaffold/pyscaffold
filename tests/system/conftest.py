import pytest

from .helpers import find_package_bin


@pytest.fixture
def tox():
    return find_package_bin("tox")


@pytest.fixture
def pre_commit():
    return find_package_bin("pre_commit", "pre-commit")


@pytest.fixture
def putup():
    return find_package_bin("pyscaffold.cli", "putup")
