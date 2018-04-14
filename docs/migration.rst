.. _migration:

=========
Migration
=========

Migrating your existing project to PyScaffold is in most cases quite easy and requires
only a few steps. We assume your project resides in the Git repository ``my_project``
and includes a package directory ``my_package`` with your Python modules.

Since you surely don't want to lose your Git history, we will just deploy a new scaffold
in the same repository and move as well as change some files. But before you start, please
make that your working tree is not dirty, i.e. all changes are committed and all important
files are under version control.

Let's start:

#. Change into the parent folder of ``my_package`` and type::

     putup old_project --force --no-skeleton -p old_package

   in order to deploy the new project structure in your repository.

#. Now move your old package folder into ``src`` with::

     git mv old_package/* src/old_package/

   Use the same technique if your project has a test folder other than ``tests`` or a
   documentation folder other than ``docs``.

#. Use ``git status`` to check for untracked files and add them with ``git add``.

#. Eventually, use ``git difftool`` to check all overwritten files for changes that need to be
   transferred. Most important is that all configuration that you may have done in ``setup.py``
   by passing parameters to ``setup(...)`` need to be moved to ``setup.cfg``. You will figure
   that out quite easily by putting your old ``setup.py`` and the new ``setup.cfg`` template side by side.
   Checkout the `documentation of setuptools`_ for more information about this conversion.
   In most cases you will not need to make changes to the new ``setup.py`` file provided by PyScaffold.
   The only exceptions are if your project uses compiled resources, e.g. Cython, or if you need to
   specify ``entry_points``.

#. In order to check that everything works, run ``python setup.py install`` and ``python setup.py sdist``.
   If those two commands don't work, check ``setup.cfg``, ``setup.py`` as well as your package under ``src`` again.
   Where all modules moved correctly? Is there maybe some ``__init__.py`` file missing?
   After these basic commands, try also to run ``python setup.py docs`` and ``python setup.py test`` to check
   that Sphinx and PyTest runs correctly.


.. _documentation of setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
