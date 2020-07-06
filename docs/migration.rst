.. _migration:

=======================
Migration to PyScaffold
=======================

Migrating your existing project to PyScaffold is in most cases quite easy and requires
only a few steps. We assume your project resides in the Git repository ``my_project``
and includes a package directory ``my_package`` with your Python modules.

Since you surely don't want to lose your Git history, we will just deploy a new scaffold
in the same repository and move as well as change some files. But before you start, please
make sure that your working tree is not dirty, i.e. all changes are committed and all important
files are under version control.

Let's start:

#. Change into the parent folder of ``my_project`` and type::

     putup my_project --force --no-skeleton -p my_package

   in order to deploy the new project structure in your repository.

#. Now change into ``my_project`` and move your old package folder into ``src`` with::

     git mv my_package/* src/my_package/

   Use the same technique if your project has a test folder other than ``tests`` or a
   documentation folder other than ``docs``.

#. Use ``git status`` to check for untracked files and add them with ``git add``.

#. Eventually, use ``git difftool`` to check all overwritten files for changes that need to be
   transferred. Most important is that all configuration that you may have done in ``setup.py``
   by passing parameters to ``setup(...)`` need to be moved to ``setup.cfg``. You will figure
   that out quite easily by putting your old ``setup.py`` and the new ``setup.cfg`` template side by side.
   Checkout the `documentation of setuptools`_ for more information about this conversion.
   In most cases you will not need to make changes to the new ``setup.py`` file provided by PyScaffold.
   The only exceptions are if your project uses compiled resources, e.g. Cython.

#. In order to check that everything works, run ``python setup.py install`` and ``python setup.py sdist``.
   If those two commands don't work, check ``setup.cfg``, ``setup.py`` as well as your package under ``src`` again.
   Were all modules moved correctly? Is there maybe some ``__init__.py`` file missing?
   After these basic commands, try also to run ``make -C docs html`` and ``py.test`` (or preferably their ``tox`` equivalents)
   to check that Sphinx and PyTest run correctly.


.. _documentation of setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
