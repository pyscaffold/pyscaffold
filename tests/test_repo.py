#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from pyscaffold import repo
from pyscaffold import structure
from fixtures import tmpdir


def test_init_commit_repo(tmpdir):
    project = "my_project"
    struct = {project: {
                  "my_file": "Some other content"
              }}
    structure.create_structure(struct)
    repo.init_commit_repo(project, struct)
    assert os.path.exists(os.path.join(project, ".git"))
