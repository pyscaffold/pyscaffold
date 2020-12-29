"""
Basic support for ANSI code formatting.
"""

import sys

ESCAPE = "\033[{:d}m"
STYLES = dict(
    clear=0,
    bold=1,
    black=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    on_black=40,
    on_red=41,
    on_green=42,
    on_yellow=43,
    on_blue=44,
    on_magenta=45,
    on_cyan=46,
    on_white=47,
)
"""Possible ``styles`` for :obj:`decorate`"""


def isatty(stream=None):
    """Detect if the given stream/stdout is part of an interactive terminal.

    Args:
        stream: optionally the stream to check

    Returns:
        bool: result of check
    """
    stream = stream or sys.stdout

    if hasattr(stream, "isatty"):
        return stream.isatty()

    return False


def init_colorama():
    """Initialize colorama if it is available.

    Returns:
        bool: result of check
    """
    try:
        import colorama  # noqa

        colorama.init()
        return True
    except ImportError:
        return False


def curses_available():
    """Check if the curses package from stdlib is available.

    Usually not available for windows, but its presence indicates that the
    terminal is capable of displaying some UI.

    Returns:
        bool: result of check
    """
    try:
        import curses  # noqa

        return True
    except ImportError:
        return False


SYSTEM_SUPPORTS_COLOR = curses_available() or init_colorama()
"""Handy indicator of the system capabilities (relies on colorama if available)"""
# Eagerly executed, in order to avoid calling colorama.init multiple times


def supports_color(stream=None):
    """Check if the stream is supposed to handle coloring.

    Returns:
        bool: result of check
    """
    return isatty(stream) and SYSTEM_SUPPORTS_COLOR


def decorate(msg, *styles):
    """Use ANSI codes to format the message.

    Args:
        msg (str): string to be formatted
        *styles (list): the remaining arguments should be strings that
            represent the 8 basic ANSI colors. ``clear`` and ``bold`` are also
            supported. For background colors use ``on_<color>``.

    Returns:
        str: styled and formatted message
    """
    if not styles:
        return msg

    styles = "".join(ESCAPE.format(STYLES[s]) for s in styles if s in STYLES)
    return styles + str(msg) + ESCAPE.format(STYLES["clear"])
