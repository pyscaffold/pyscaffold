# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import contextlib
from os.path import join as join_path

import git


def git_tree_add(repo, struct, prefix=None):
    if prefix is None:
        prefix = ""
    for name, content in struct.iteritems():
        if isinstance(content, str):
            repo.index.add([join_path(prefix, name)])
        elif isinstance(content, dict):
            git_tree_add(repo, struct[name], prefix=join_path(prefix, name))
        else:
            raise RuntimeError("Don't know what to do with content type {}."
                               .format(type(content)))


@contextlib.contextmanager
def chdir(path):
    curr_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(curr_dir)


def init_commit_repo(project, struct):
    repo = git.repo.Repo.init(project)
    with chdir(project):
        git_tree_add(repo, struct[project])
        repo.index.write()
        repo.index.commit(message="Initial commit")
