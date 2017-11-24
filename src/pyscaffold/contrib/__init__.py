# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold sourcecode itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often 
than not, see issues #71 and #72.

1) setuptools_scm

This package was added with the help of ``git subtree`` (git version 1.7.11 and above)::

    git remote add -f -t master --no-tags setuptools_scm https://github.com/pypa/setuptools_scm.git
    git fetch setuptools_scm
    git checkout setuptools_scm/master
    git subtree split -P setuptools_scm -b temporary-split-branch
    git checkout master
    git subtree add --squash -P src/pyscaffold/contrib/setuptools_scm temporary-split-branch
    git branch -D temporary-split-branch

Updating works with the following code. Instead of ``setuptools/master`` it's better to directly
address the SHA1 of a certain release tag::

    git checkout setuptools_scm/master
    git subtree split -P setuptools_scm -b temporary-split-branch
    git checkout master
    git subtree merge --squash -P src/pyscaffold/contrib/setuptools_scm temporary-split-branch
    # Now fix any conflicts if we have modified anything within setuptools_scm
    git branch -D temporary-split-branch

Using ``subtree`` instead of git's ``submodule`` had several advantages.
For more details check out:
https://stackoverflow.com/questions/23937436/add-subdirectory-of-remote-repo-with-git-subtree

2) six

Since this package consists only of a single module, namely six.py, it was just copied over.

3) pytest-runner

Since this package consists only of a single module, namely six.py, it was just copied over.
"""
from __future__ import division, print_function, absolute_import
