.. _updating:

===============================
Updating from Previous Versions
===============================

When updating a project generated with the same major version of PyScaffold
[#up1]_, running ``putup --update`` should be enough to get you going.
However updating from previous major versions of PyScaffold will probably
require some manual adjustments. The following sections describe how to update
from one major version into the following one.

.. warning::
   Before updating make sure to commit all the pending changes in your
   repository. If something does not work exactly how you expected after the
   update, please revise the changes using a ``diff`` and perform the necessary
   corrections.


Updates from PyScaffold 2 to PyScaffold 3
-----------------------------------------

Since the overall structure of a project set up with PyScaffold 2 differs quite
much from a project generated with PyScaffold 3 it is not possible to just use
the ``--update`` parameter. Still with some manual efforts an update from
a scaffold generated with PyScaffold 2 to PyScaffold 3's scaffold is quite easy.
Assume the name of our project is ``old_project`` with a package called
``old_package`` and no namespaces then just:

1) make sure your worktree is not dirty, i.e. commit all your changes,
2) run ``putup old_project --force --no-skeleton -p old_package`` to generate
   the new structure inplace and ``cd`` into your project,
3) move with ``git mv old_package/* src/old_package/ --force`` your old package
   over to the new ``src`` directory,
4) check ``git status`` and add untracked files from the new structure,
5) use ``git difftool`` to check all overwritten files, especially ``setup.cfg``,
   and transfer custom configurations from the old structure to the new,
6) check if ``python setup.py test sdist`` works and commit your changes.


Updates from PyScaffold 3 to PyScaffold 4
-----------------------------------------

Most of the time, updating from PyScaffold 3 should be completely automatic.
However, since in version 4 we have adopted Python's new standards for
packaging (`PEP 517`_/`PEP 518`_), you might find the new build process incompatible.

If that is the case, you can use the ``--no-pyproject`` flag to keep using the
legacy behaviour. You will need, though, to manually remove PyScaffold from
your build dependencies (``setup_requires`` in ``setup.cfg``) and add
`setuptools_scm`_.

Please note that the use of ``setup_requires`` is discouraged. If you are using
``pyproject.toml``, PyScaffold will remove this field automatically and transfer
the dependencies to the ``pyproject.toml :: build-system.requires`` field.
However, if you are using legacy builds we will not remove it. You might be
interested in doing that yourself and using other tools like `tox`_ to build
your project with the correct dependencies in place. With `tox`_ you can specify a
``build`` testenv with the `skip_install`_ option and the required build time
dependencies in ``deps``.

.. [#up1] PyScaffold uses 3 numbers for its version: ``MAJOR.MINOR.PATCH``
   (when the numbers on the right are missing, just assume them as being 0),
   so PyScaffold 3.1.2 has the same major version as PyScaffold 3.3.1, but not
   PyScaffold 4.

.. _PEP 517: https://www.python.org/dev/peps/pep-0517/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _setuptools_scm: https://pypi.python.org/pypi/setuptools_scm/
.. _tox: https://tox.readthedocs.org/
.. _skip_install: https://tox.readthedocs.io/en/latest/config.html#conf-skip_install
