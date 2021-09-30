from pathlib import Path
from shutil import copytree

from pyscaffold import cli
from pyscaffold import file_system as fs
from pyscaffold import shell


def copy_example(name, target_dir) -> Path:
    example = Path(__file__).parent / "examples" / name
    target = Path(target_dir, name)
    return Path(copytree(str(example), str(target)))


def test_issue506(tmpfolder):
    # Given a project exists with the same `setup.cfg` from issue506
    with fs.chdir(copy_example("issue-506", tmpfolder)):
        shell.git("init", ".")
        shell.git("add", ".")
        shell.git("commit", "-m", "Add code before update")
        # when we run the update
        cli.run([".", "--update", "--force"])
        # then no error should be raised when updating
        # and the extension should load correctly (e.g. namespace)
        assert Path("src/pyscaffoldext/company/__init__.py").exists()
        assert not Path("src/pyscaffoldext/__init__.py").exists()
        assert not Path("src/company").exists()
