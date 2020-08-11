try:
    from importlib.metadata import PackageNotFoundError, version  # type: ignore
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"
