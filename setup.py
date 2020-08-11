"""Setup file for PyScaffold."""
from setuptools import setup

if __name__ == "__main__":
    try:
        setup(use_scm_version={"version_scheme": "post-release"})
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools with: "
            "`pip install -U setuptools`\n\n"
        )
        raise
