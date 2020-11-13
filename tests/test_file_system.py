import logging
import os
import re
import stat

from pyscaffold import file_system as fs

from .helpers import temp_umask, uniqpath, uniqstr


def test_tmpfile(tmpfolder):
    with fs.tmpfile(suffix=".foo.bar", dir=str(tmpfolder)) as tmp:
        path = str(tmp)
        assert path.endswith(".foo.bar")
        assert tmp.exists()

    assert not tmp.exists()


def test_chdir(caplog, tmpdir, isolated_logger):
    caplog.set_level(logging.INFO)
    curr_dir = os.getcwd()
    dname = uniqstr()  # Use a unique name to get easily identifiable logs
    temp_dir = str(tmpdir.mkdir(dname))
    with fs.chdir(temp_dir, log=True):
        new_dir = os.getcwd()
    assert new_dir == os.path.realpath(temp_dir)
    assert curr_dir == os.getcwd()
    assert curr_dir != new_dir
    logs = caplog.text
    assert re.search("chdir.+" + dname, logs)


def test_pretend_chdir(caplog, tmpdir):
    caplog.set_level(logging.INFO)
    curr_dir = os.getcwd()
    dname = uniqstr()  # Use a unique name to get easily identifiable logs
    temp_dir = str(tmpdir.mkdir(dname))
    with fs.chdir(temp_dir, pretend=True):
        new_dir = os.getcwd()
    assert new_dir == curr_dir  # the directory is not changed
    assert curr_dir == os.getcwd()
    logs = caplog.text
    assert re.search("chdir.+" + dname, logs)


def test_create_file(tmpfolder):
    file = fs.create_file("a-file.txt", "content")
    assert file.is_file()
    assert tmpfolder.join("a-file.txt").read() == "content"


def test_pretend_create_file(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    fname = uniqstr()  # Use a unique name to get easily identifiable logs
    # When a file is created with pretend=True,
    file = fs.create_file(fname, "content", pretend=True)
    # Then it should not be written to the disk,
    assert not file.exists()
    assert tmpfolder.join(fname).check() is False
    # But the operation should be logged
    logs = caplog.text
    assert re.search("create.+" + fname, logs)


def test_create_directory(tmpfolder):
    folder = fs.create_directory("a-dir")
    assert folder.is_dir()
    assert tmpfolder.join("a-dir").check(dir=1)


def test_pretend_create_directory(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    dname = uniqstr()  # Use a unique name to get easily identifiable logs
    # When a directory is created with pretend=True,
    folder = fs.create_directory(dname, pretend=True)
    # Then it should not appear in the disk,
    assert not folder.exists()
    assert tmpfolder.join(dname).check() is False
    # But the operation should be logged
    logs = caplog.text
    assert re.search("create.+" + dname, logs)


def test_chmod(tmpfolder):
    _ = tmpfolder  # just for chdir

    # Windows have problems with executable bits, so let's just exercise R and W
    with temp_umask(0o333):
        file = uniqpath()
        file.touch()
        assert stat.S_IMODE(file.stat().st_mode) == 0o444
        fs.chmod(file, 0o666)
        assert stat.S_IMODE(file.stat().st_mode) == 0o666


def test_pretend_chmod(tmpfolder, caplog):
    _ = tmpfolder  # just for chdir
    caplog.set_level(logging.INFO)

    # Windows have problems with executable bits, so let's just exercise R and W
    with temp_umask(0o333):
        file = uniqpath()
        file.touch()
        assert stat.S_IMODE(file.stat().st_mode) == 0o444
        # When calling chmod on a file with pretend
        fs.chmod(file, 0o777, pretend=True)
        # It should not change access permissions
        assert stat.S_IMODE(file.stat().st_mode) == 0o444
        # But the operation should be logged
        logs = caplog.text
        assert re.search(f"chmod 777.+{file}", logs)


def test_move(tmpfolder):
    # Given a file or directory exists,
    tmpfolder.join("a-file.txt").write("text")
    tmpfolder.join("a-folder").ensure_dir()
    tmpfolder.join("a-folder/another-file.txt").write("text")
    # When it is moved,
    tmpfolder.join("a-dir").ensure_dir()
    fs.move("a-file.txt", target="a-dir")
    fs.move("a-folder", target="a-dir")
    # Then the original path should not exist
    assert not tmpfolder.join("a-file.txt").check()
    assert not tmpfolder.join("a-folder").check()
    # And the new path should exist
    assert tmpfolder.join("a-dir/a-file.txt").check()
    assert tmpfolder.join("a-dir/a-folder/another-file.txt").check()


def test_move_multiple_args(tmpfolder):
    # Given several files exist,
    tmpfolder.join("a-file.txt").write("text")
    tmpfolder.join("another-file.txt").write("text")
    assert not tmpfolder.join("a-dir/a-file.txt").check()
    assert not tmpfolder.join("a-dir/another-file.txt").check()
    # When they are moved together,
    tmpfolder.join("a-dir").ensure_dir()
    fs.move("a-file.txt", "another-file.txt", target="a-dir")
    # Then the original paths should not exist
    assert not tmpfolder.join("a-file.txt").check()
    assert not tmpfolder.join("another-file.txt").check()
    # And the new paths should exist
    assert tmpfolder.join("a-dir/a-file.txt").read() == "text"
    assert tmpfolder.join("a-dir/another-file.txt").read() == "text"


def test_move_non_dir_target(tmpfolder):
    # Given a file exists,
    tmpfolder.join("a-file.txt").write("text")
    assert not tmpfolder.join("another-file.txt").check()
    # When it is moved,
    fs.move("a-file.txt", target="another-file.txt")
    # Then the original path should not exist
    assert not tmpfolder.join("a-file.txt").check()
    # And the new path should exist
    assert tmpfolder.join("another-file.txt").read() == "text"

    # Given a dir exists,
    tmpfolder.join("a-dir").ensure_dir()
    tmpfolder.join("a-dir/a-file.txt").write("text")
    assert not tmpfolder.join("another-dir/a-file.txt").check()
    # When it is moved to a path that do not exist yet,
    fs.move("a-dir", target="another-dir")
    # Then the dir should be renamed.
    assert not tmpfolder.join("a-dir").check()
    assert tmpfolder.join("another-dir/a-file.txt").read() == "text"


def test_move_log(tmpfolder, caplog):
    caplog.set_level(logging.INFO)
    fname1 = uniqstr()  # Use a unique name to get easily identifiable logs
    fname2 = uniqstr()
    dname = uniqstr()
    # Given a file or directory exists,
    tmpfolder.join(fname1).write("text")
    tmpfolder.join(fname2).write("text")
    # When it is moved without log kwarg,
    tmpfolder.join(dname).ensure_dir()
    fs.move(fname1, target=dname)
    # Then no log should be created.
    logs = caplog.text
    assert not re.search(f"move.+{fname1}.+to.+{dname}", logs)
    # When it is moved with log kwarg,
    fs.move(fname2, target=dname, log=True)
    # Then log should be created.
    logs = caplog.text
    assert re.search(f"move.+{fname2}.+to.+{dname}", logs)


def test_pretend_move(tmpfolder):
    # Given a file or directory exists,
    tmpfolder.join("a-file.txt").write("text")
    tmpfolder.join("another-file.txt").write("text")
    # When it is moved without pretend kwarg,
    tmpfolder.join("a-dir").ensure_dir()
    fs.move("a-file.txt", target="a-dir")
    # Then the src should be moved
    assert tmpfolder.join("a-dir/a-file.txt").check()
    # When it is moved with pretend kwarg,
    fs.move("another-file.txt", target="a-dir", pretend=True)
    # Then the src should not be moved
    assert not tmpfolder.join("a-dir/another-file.txt").check()
    assert tmpfolder.join("another-file.txt").check()


def test_rm_rf(tmp_path):
    # Given nested dirs and files exist
    nested_dir = tmp_path / "dir1/dir2/dir3"
    nested_dir.mkdir(parents=True, exist_ok=True)
    nested_file = nested_dir / "file"
    nested_file.write_text("text")
    # When rm_rf is called
    fs.rm_rf(tmp_path / "dir1")
    # Then nothing should be left
    assert not nested_file.exists()
    assert not nested_dir.exists()
    assert not nested_dir.parent.exists()

    # Given a file exists
    file = tmp_path / "answer.txt"
    file.write_text("42")
    assert file.read_text() == "42"
    # When rm_rf is called with files
    fs.rm_rf(file)
    # Then no exception is raised and the file is removed
    assert not file.exists()


def test_pretend_rm_rf(tmp_path, caplog):
    # Given nested dirs and files exist
    dname = uniqstr()  # Use a unique name to get easily identifiable logs
    nested_dir = tmp_path / dname / "dir2/dir3"
    nested_dir.mkdir(parents=True, exist_ok=True)
    nested_file = nested_dir / "file"
    nested_file.write_text("text")
    # When rm_rf is called with pretend
    fs.rm_rf(tmp_path / dname, pretend=True)
    # Then nothing should change
    assert nested_file.exists()
    assert nested_dir.exists()
    assert nested_dir.parent.exists()
    # But the operation should be logged
    logs = caplog.text
    assert re.search("remove.+" + dname, logs)
