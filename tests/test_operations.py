import os
import stat

from pyscaffold.operations import (
    add_permissions,
    create,
    no_overwrite,
    remove,
    skip_on_update,
)

from .helpers import temp_umask, uniqpath


def test_create(monkeypatch):
    created = {}

    def spy(path, *_1, **_2):
        created.update({path: True})

    monkeypatch.setattr("pyscaffold.file_system.create_file", spy)

    # When content is string, execute, even if it is empty
    for contents in ("contents", ""):
        path = uniqpath()
        create(path, contents, {})
        assert created[path]

    # When content is None, skip
    path = uniqpath()
    create(path, None, {})
    assert path not in created


def test_remove(monkeypatch):
    removed = {}

    def spy(path, *_1, **_2):
        removed.update({path: True})

    monkeypatch.setattr("pathlib.Path.exists", lambda _: True)
    monkeypatch.setattr("pyscaffold.file_system.rm_rf", spy)

    for contents in ("contents", "", None):
        path = uniqpath()
        remove(path, contents, {})
        assert removed[path]

    # Non existing paths are simply skipped
    monkeypatch.setattr("pathlib.Path.exists", lambda _: False)
    path = uniqpath()
    assert remove(path, contents, {}) is None
    assert path not in removed


def test_skip_on_update(monkeypatch):
    SKIP_ON_UPDATE = skip_on_update(lambda *_: path)

    # When update is False, execute
    opts = {"update": False}
    path = uniqpath()
    assert SKIP_ON_UPDATE(path, "contents", opts) == path

    # When update is True, skip, even if file does not exist
    opts = {"update": True}
    path = uniqpath()
    for existing in (True, False):
        with monkeypatch.context() as patch:
            patch.setattr("pathlib.Path.exists", lambda _: existing)
            assert SKIP_ON_UPDATE(path, "contents", opts) is None

    # When force is True, execute, even if file exists
    opts = {"update": True, "force": True}
    path = uniqpath()
    for existing in (True, False):
        with monkeypatch.context() as patch:
            patch.setattr("pathlib.Path.exists", lambda _: existing)
            assert SKIP_ON_UPDATE(path, "contents", opts) == path


def test_no_overwrite(monkeypatch):
    NO_OVERWRITE = no_overwrite(lambda *_: path)

    # When file does not exist, execute
    path = uniqpath()
    with monkeypatch.context() as patch:
        patch.setattr("pathlib.Path.exists", lambda _: False)
        assert NO_OVERWRITE(path, "contents", {}) == path

    # When file exists, skip
    path = uniqpath()
    with monkeypatch.context() as patch:
        patch.setattr("pathlib.Path.exists", lambda _: True)
        assert NO_OVERWRITE(path, "contents", {}) is None

    # When force is True, execute, even if file exists
    opts = {"force": True}
    path = uniqpath()
    for existing in (True, False):
        with monkeypatch.context() as patch:
            patch.setattr("pathlib.Path.exists", lambda _: existing)
            assert NO_OVERWRITE(path, "contents", opts) == path


def test_add_permissions(tmpfolder):
    _ = tmpfolder  # Just used for chdir

    with temp_umask(0o333):
        # Without add_permissions, mode should be the same as umask
        path = uniqpath()
        create(path, "contents", {})
        assert stat.S_IMODE(path.stat().st_mode) == 0o444

        # With add_permissions, mode should have the extra bits
        path = uniqpath()
        if os.name == "posix":
            add_permissions(stat.S_IXOTH)(path, "contents", {})
            # ^  executable permissions should be the most common use case
            assert stat.S_IMODE(path.stat().st_mode) == 0o445
        else:
            add_permissions(stat.S_IWRITE)(path, "contents", {})
            # ^  windows executables work in a complete different way, so we just do a
            #    basic test with writeable access, just for the sake of completeness
            assert stat.S_IMODE(path.stat().st_mode) == 0o666
