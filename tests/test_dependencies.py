from pyscaffold import dependencies as deps


def test_split():
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
    assert deps.split(
        "\n    pyscaffold>=42.1.0,<43.0;python_version>='3.4'; appdirs==1"
    ) == ["pyscaffold>=42.1.0,<43.0;python_version>='3.4'", "appdirs==1"]
    assert deps.split(
        "\n    pyscaffold>=42.1.0,<43.0; python_version>='3.4'; appdirs==1"
    ) == ["pyscaffold>=42.1.0,<43.0; python_version>='3.4'", "appdirs==1"]


def test_deduplicate():
    # no duplication => no effect
    assert deps.deduplicate(["pyscaffold>=4,<5", "appdirs"]) == [
        "pyscaffold>=4,<5",
        "appdirs",
    ]
    # duplicated => the last one wins
    assert deps.deduplicate(
        ["pyscaffold>=4,<5", "pyscaffold~=3.2", "pyscaffold==0"]
    ) == ["pyscaffold==0"]
    assert deps.deduplicate(
        ["pyscaffold==0", "pyscaffold>=4,<5", "pyscaffold~=3.2"]
    ) == ["pyscaffold~=3.2"]


def test_remove():
    assert (
        deps.remove(
            ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
            ["appdirs"],
        )
        == ["pyscaffold>=42.1.0,<43.0", "cookiecutter<8", "mypkg~=9.0"]
    )
    assert (
        deps.remove(
            ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8", "mypkg~=9.0"],
            {"mypkg": 0},
        )
        == ["pyscaffold>=42.1.0,<43.0", "appdirs==1", "cookiecutter<8"]
    )


def test_add():
    own_deps = [
        "setuptools_scm>=1.2.5,<2",
        "pyscaffold>=42.1.0,<43",
        "django>=5.3.99999,<6",
    ]
    # No intersection
    assert deps.add(["appdirs==1", "cookiecutter<8", "mypkg~=9.0"], own_deps) == [
        "appdirs==1",
        "cookiecutter<8",
        "mypkg~=9.0",
        "setuptools_scm>=1.2.5,<2",
        "pyscaffold>=42.1.0,<43",
        "django>=5.3.99999,<6",
    ]
    # With intersection => own_deps win
    assert deps.add(["appdirs==1", "pyscaffold<8", "mypkg~=9.0"], own_deps) == [
        "appdirs==1",
        "pyscaffold>=42.1.0,<43",
        "mypkg~=9.0",
        "setuptools_scm>=1.2.5,<2",
        "django>=5.3.99999,<6",
    ]
