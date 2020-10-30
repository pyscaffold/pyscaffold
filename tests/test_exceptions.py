import logging
import re
import sys

import pytest

from pyscaffold.exceptions import ErrorLoadingExtension, exceptions2exit
from pyscaffold.log import logger

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


def test_exceptions2exit_verbose(capsys):
    @exceptions2exit([RuntimeError])
    def func(_):
        logger.level = logging.DEBUG
        raise RuntimeError("Exception raised")

    with pytest.raises(SystemExit):
        func(1)
    error = capsys.readouterr().err
    match = re.search(r"raise RuntimeError", error)
    assert match


def test_error_loading_external_extension():
    # Assert the error message displays the correct python package name
    extension = "pyscaffoldext.fake.extension"

    # Extension name is given directly
    ex = ErrorLoadingExtension(extension)
    assert "an error loading 'pyscaffoldext-fake'" in str(ex)

    # Entrypoint is given
    fake = EntryPoint("fake", f"{extension}:Fake", "pyscaffold.cli")
    ex = ErrorLoadingExtension(entry_point=fake)
    assert "an error loading 'pyscaffoldext-fake'" in str(ex)
