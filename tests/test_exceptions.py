import logging
import re

import pytest

from pyscaffold.exceptions import exceptions2exit
from pyscaffold.log import logger


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
