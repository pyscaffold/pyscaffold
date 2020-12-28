import argparse
from textwrap import dedent

import pytest

from pyscaffold import api, cli, info, templates
from pyscaffold.extensions import config

from ..helpers import ArgumentParser
from .helpers import make_extension

# ---- "Isolated" tests ----


@pytest.fixture
def default_file(fake_config_dir):
    return fake_config_dir / "default.cfg"


def parse(*args, set_defaults=None):
    parser = ArgumentParser()
    parser.set_defaults(**(set_defaults or {}))
    config.Config().augment_cli(parser)
    return vars(parser.parse_args(args))


def test_no_cli_opts(default_file):
    # When no --config or --save-config is passed
    cli_opts = parse()

    # Then no save_config or config_files should be found in the opts
    assert "save_files" not in cli_opts

    # and config_files will be bootstraped with an empty list
    # if the default file does not exist
    opts = api.bootstrap_options(cli_opts)
    assert opts["config_files"] == []

    # or config_files will be bootstraped with the
    # default file if it exists
    default_file.write_text("[pyscaffold]\n")
    opts = api.bootstrap_options(cli_opts)
    assert opts["config_files"] == [default_file]


def test_missing_config():
    # When the --config opt is passed without a value, we have an error
    with pytest.raises((argparse.ArgumentError, TypeError, SystemExit)):
        # ^  TypeError happens because argparse tries to iterate over the --config opts
        #    since it is marked with nargs='+'
        #    ArgumentError and SystemExit might happen depending on the version
        #    of Python when there is a parse error.
        parse("--config")


def test_config_opts(default_file, fake_config_dir):
    files = []
    for j in range(3):
        file = fake_config_dir / f"test{j}.cfg"
        file.write_text("[pyscaffold]\n")
        files.append(file)

    # --config can be passed with 1 value
    opts = parse("--config", str(files[0]))
    assert opts["config_files"] == files[:1]

    # --config can be passed with many
    opts = parse("--config", *map(str, files))
    assert opts["config_files"] == files

    # after bootstrap_options, the given files are kept
    # and the default is not included
    opts = api.bootstrap_options(opts)
    assert default_file not in opts["config_files"]
    assert opts["config_files"] == files


def test_no_config():
    opts = parse("--no-config")
    assert opts["config_files"] == api.NO_CONFIG

    # Even after bootstrap_options
    opts = api.bootstrap_options(opts)
    assert opts["config_files"] == api.NO_CONFIG


def test_no_config_conflict(fake_config_dir):
    file = fake_config_dir / "test_no_config.cfg"
    file.write_text("[pyscaffold]\n")
    with pytest.raises(SystemExit):
        parse("--no-config", "--config", str(file))


def test_save_config(default_file, fake_config_dir):
    # With no value the default_file is used
    opts = parse("--save-config")
    assert opts["save_config"] == default_file

    # With a value, the value is used
    other_file = fake_config_dir / "other.cfg"
    opts = parse("--save-config", str(other_file))
    assert opts["save_config"] == other_file


# ---- Integration tests ----


def test_save_action(default_file):
    # When the file does not exist
    assert not default_file.exists()
    opts = dict(author="author", email="email", license="MPL-2.0")
    config.save({}, {**opts, "save_config": default_file})
    # it will create a valid file from the point of view of parsing
    assert default_file.exists()
    parsed = info.project({}, default_file)
    assert all(parsed[k] == v for k, v in opts.items())
    # and the file will contain instructions / references
    assert "pyscaffold.org" in default_file.read_text()


def existing_config(file):
    text = dedent(
        """\
        [metadata]
        author = John Doe
        author-email = john.joe@fmail.com
        license = gpl3

        [pyscaffold]
        # Comment
        version = 3.78
        extensions =
            namespace
            tox
            cirrus
        namespace = my_namespace.my_sub_namespace
        """
    )
    file.write_text(text)
    return file


def test_save_action_existing_file(default_file, monkeypatch):
    # Given default values that differ a bit from the given opts
    monkeypatch.setattr(info, "username", lambda *_: "John Doe")
    monkeypatch.setattr(info, "email", lambda *_: "email")
    monkeypatch.setitem(api.DEFAULT_OPTIONS, "license", "MPL-2.0")
    opts = dict(author="author", email="email", license="MPL-2.0")
    # When the file exists and new config is saved
    existing_config(default_file)
    config.save({}, {**opts, "save_config": default_file})
    # Then metadata that differs from default will change
    expected = dict(author="author", email="john.joe@fmail.com", license="GPL-3.0-only")
    parsed = info.project({}, default_file)
    assert all(parsed[k] == v for k, v in expected.items())


def test_save_action_additional_extensions(default_file):
    # Given the file exists
    existing_config(default_file)
    # When the new config is saved with new extensions
    opts = dict(author="author", email="email", license="MPL-2.0", my_extension1_opt=5)
    extensions = [
        make_extension("MyExtension1"),
        make_extension("MyExtension2"),
        make_extension("MyExtension3", persist=False),
    ]
    config.save({}, {**opts, "save_config": default_file, "extensions": extensions})
    # The old ones are kept and the new ones are added,
    # unless they specify persist=False
    parsed = info.read_setupcfg(default_file).to_dict()["pyscaffold"]
    print(default_file.read_text())
    expected = {"namespace", "tox", "cirrus", "my_extension1", "my_extension2"}
    assert templates.parse_extensions(parsed["extensions"]) == expected
    assert parsed["namespace"] == "my_namespace.my_sub_namespace"
    # Extension related opts are also saved
    assert int(parsed["my_extension1_opt"]) == 5


def test_cli_with_save_config(default_file, tmpfolder):
    # Given a global config file does not exist
    assert not default_file.exists()
    # when the CLI is invoked with --save-config
    cli.main("proj -l MPL-2.0 --namespace ns --cirrus --save-config".split())
    # then the file will be created accordingly
    assert default_file.exists()
    parsed = info.read_setupcfg(default_file).to_dict()
    assert parsed["metadata"]["license"] == "MPL-2.0"
    assert parsed["pyscaffold"]["namespace"] == "ns"
    assert "cirrus" in parsed["pyscaffold"]["extensions"]
    # and since the config extension has persist = False, it will not be stored
    assert "config" not in parsed["pyscaffold"]["extensions"]


def test_cli_with_save_config_and_pretend(default_file, tmpfolder):
    # Given a global config file does not exist
    assert not default_file.exists()
    # when the CLI is invoked with --save-config and --pretend
    cli.main("proj --pretend -l MPL-2.0 --namespace ns --cirrus --save-config".split())
    # then the file should not be created
    assert not default_file.exists()
    # (or even the project)
    assert not (tmpfolder / "proj").exists()
