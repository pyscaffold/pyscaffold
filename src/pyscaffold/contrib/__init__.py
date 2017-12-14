# -*- coding: utf-8 -*-
"""
Contribution packages used by PyScaffold

All packages inside ``contrib`` are external packages that come with their
own licences and are not part of the PyScaffold source code itself.
The reason for shipping these dependencies directly is to avoid problems in
the resolution of ``setup_requires`` dependencies that occurred more often 
than not, see issues #71 and #72.

Currently the contrib packages are:

1) setuptools_scm v1.15.6
2) six 1.11.0
3) pytest-runner 3.0

The packages/modules were just copied over.
"""
from __future__ import division, print_function, absolute_import
