from pkg_resources import parse_version

from pyscaffold import dependencies as deps


def test_is_dep_included():
    requirements = {
        "setuptools_scm": "some.version",
        "pyscaffold": "42.0",
        "django": "0",
    }
    assert deps.is_included("setuptools_scm>=34", requirements)
    assert deps.is_included("pyscaffold>=5.34.5,<=42", requirements)
    assert deps.is_included("django", requirements)
    assert not deps.is_included("appdirs==1", requirements)
    assert not deps.is_included("cookiecutter<8", requirements)
    assert not deps.is_included("mypkg~=9.0", requirements)


def test_split_deps():
    assert deps.split(
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    appdirs==1"
        "\n    cookiecutter<8"
        "\n    mypkg~=9.0"
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.split(
        "\n    pyscaffold>=42.1.0,<43.0;appdirs==1"
        "\n    cookiecutter<8;mypkg~=9.0\n\n"
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.split(
        "pyscaffold>=42.1.0,<43.0; appdirs==1; cookiecutter<8; mypkg~=9.0; "
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"]


def test_remove_deps():
    assert deps.remove(
        ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        ["appdirs"],
    ) == ["pyscaffold>=42.1.0,<43.0", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.remove(
        ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        {"mypkg": 0},
    ) == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8"]


def test_get_requirements_str():
    own_deps = {
        "setuptools_scm": parse_version("1.2.5"),
        "pyscaffold": parse_version("42.1.0"),
        "django": parse_version("5.3.99999"),
    }
    # No intersection
    assert deps.get_requirements_str(
        ["appdirs==1", "cookiecutter<8", "mypkg~=9.0"], own_deps
    ) == (
        "\n    setuptools_scm>=1.2.5,<2.0"
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    django>=5.3.99999,<6.0"
        "\n    appdirs==1"
        "\n    cookiecutter<8"
        "\n    mypkg~=9.0"
    )
    # With intersection => own_deps win
    assert deps.get_requirements_str(
        ["appdirs==1", "pyscaffold<8", "mypkg~=9.0"], own_deps
    ) == (
        "\n    setuptools_scm>=1.2.5,<2.0"
        "\n    pyscaffold>=42.1.0,<43.0"
        "\n    django>=5.3.99999,<6.0"
        "\n    appdirs==1"
        "\n    mypkg~=9.0"
    )
