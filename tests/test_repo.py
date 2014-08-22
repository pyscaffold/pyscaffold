#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from pyscaffold import repo
from pyscaffold import structure

import pytest

from .fixtures import tmpdir

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_init_commit_repo(tmpdir):
    project = "my_project"
    struct = {project: {
        "my_file": "Some other content",
        "my_dir": {"my_file": "Some more content"},
        "dummy": None}
    }
    structure.create_structure(struct)
    dummy_file = os.path.join(project, "dummy")
    with open(dummy_file, 'w'):
        os.utime(dummy_file, None)
    repo.init_commit_repo(project, struct)
    assert os.path.exists(os.path.join(project, ".git"))


def test_init_commit_repo_with_wrong_structure(tmpdir):
    project = "my_project"
    struct = {project: {
        "my_file": type("StrangeType", (object,), {})}}
    os.mkdir(project)
    with pytest.raises(RuntimeError):
        repo.init_commit_repo(project, struct)
