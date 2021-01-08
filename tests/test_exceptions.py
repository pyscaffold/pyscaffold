import logging
import re
import sys

import pytest

from pyscaffold.exceptions import ErrorLoadingExtension, exceptions2exit

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import EntryPoint  # pragma: no cover
else:
    from importlib_metadata import EntryPoint  # pragma: no cover


def test_exceptions2exit():
    @exceptions2exit([RuntimeError])
    def func(_):
        raise RuntimeError("Exception raised")

    with pytest.raises(SystemExit):
        func(1)


def test_exceptions2exit_verbose(capsys, monkeypatch):
    @exceptions2exit([RuntimeError])
    def func(_):
        raise RuntimeError("Exception raised")

    monkeypatch.setattr("pyscaffold.cli.get_log_level", lambda: logging.DEBUG)
    with pytest.raises(SystemExit):
        func(1)

    error = capsys.readouterr().err
    match = re.search(r"raise RuntimeError", error)
    assert match


def test_error_loading_external_extension():
    # Assert the error message displays some meaningful text
    extension = "pyscaffoldext.fake.extension"

    # Extension name is given directly
    ex = str(ErrorLoadingExtension(extension))
    assert "an error loading" in ex
    assert "fake" in ex

    # Entrypoint is given
    fake = EntryPoint("fake", f"{extension}:Fake", "pyscaffold.cli")
    ex = str(ErrorLoadingExtension(entry_point=fake))
    assert "an error loading" in ex
    assert "fake" in ex
