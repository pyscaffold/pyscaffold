from importlib import reload
from io import StringIO

import pytest

from pyscaffold import termui


@pytest.fixture(scope="module")
def after():
    # Reload termui after tests to ensure constants are calculated
    # with original logic (without mocks).
    yield
    reload(termui)


@pytest.fixture
def fake_tty(monkeypatch):
    # NOTE:
    # This fixture is a workaround for the limitations of pytest stdout/stderr
    # capture.
    # To be realistic we should test termui against real TTY devices,
    # and maybe the best way of doing it is just using the stdout/stderr
    # in the terminal.
    # Since pytest buffers the output, we need to rely on the `disabled`
    # contextmanager of the `capsys` fixture.
    # However, this currently doesn't work with pytest-xdist (see
    # https://github.com/pytest-dev/pytest/issues/1991).
    # So if we intend to run our tests in parallel, we have to gave up on it :(
    stream = StringIO()
    monkeypatch.setattr(stream, "isatty", lambda *_: True)

    return stream


def test_isatty_file(tmpfolder, orig_isatty):
    file = tmpfolder.join("file.txt").ensure().open()
    assert not termui.isatty(file)


def test_isatty_buffer(orig_isatty):
    assert not termui.isatty(StringIO())


def test_isatty_random_obj(orig_isatty):
    assert not termui.isatty([1, 2, 3])


def test_isatty_tty(fake_tty, orig_isatty):
    assert termui.isatty(fake_tty)


def test_support_with_curses_no_colorama(
    fake_tty, curses_mock, no_colorama_mock, orig_isatty
):
    reload(termui)  # ensure mocks side effects
    assert termui.SYSTEM_SUPPORTS_COLOR
    assert termui.supports_color(fake_tty)


def test_support_no_curses_with_colorama(
    fake_tty, no_curses_mock, colorama_mock, orig_isatty
):
    reload(termui)  # ensure mocks side effects
    assert termui.SYSTEM_SUPPORTS_COLOR
    assert termui.supports_color(fake_tty)


def test_support_with_curses_with_colorama(
    fake_tty, curses_mock, colorama_mock, orig_isatty
):
    reload(termui)  # ensure mocks side effects
    assert termui.SYSTEM_SUPPORTS_COLOR
    assert termui.supports_color(fake_tty)


def test_support_no_colorama_no_curses(
    fake_tty, no_curses_mock, no_colorama_mock, orig_isatty
):
    reload(termui)  # ensure mocks side effects
    assert not termui.SYSTEM_SUPPORTS_COLOR
    assert not termui.supports_color(fake_tty)


def test_decorate():
    # When styles are passed,
    text = termui.decorate("text", "red", "bold")
    # then they should be present in the response
    assert "\033[1m" in text  # bold
    assert "\033[31m" in text  # red
    assert "\033[0m" in text  # clear

    # When styles are not passed,
    text = termui.decorate("text")
    # then the text should not contain ansi codes
    assert "\033[1m" not in text  # bold
    assert "\033[31m" not in text  # red
    assert "\033[0m" not in text  # clear
    assert text == "text"
