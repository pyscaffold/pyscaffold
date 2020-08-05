.. _faq:

==========================
Frequently Asked Questions
==========================

In case you have a general question that is not answered here, consider submitting a `new issue`_.

1. **Why would I use PyScaffold instead of Cookiecutter?**

   PyScaffold is focused on a good out-of-the-box experience for developing distributable Python packages (exclusively).
   The idea is to standardize the structure of Python packages. Thus, PyScaffold sticks to

       "There should be one-- and preferably only one --obvious way to do it."

   from the `Zen of Python`_. The long-term goal is that PyScaffold becomes for Python what `Cargo`_ is for `Rust`_.
   Still, with the help of PyScaffold's :ref:`extension system <extensions>` customizing a project scaffold is possible.

   Cookiecutter on the other hand is a really flexible templating tool that allows you to define own templates according
   to your needs. Although some standard templates are provided that will give you quite similar results as PyScaffold,
   the overall goal of the project is quite different.

|

2. **Does my project depend on PyScaffold when I use it to set my project up?**

   Starting from version 4, your package is completely independent from PyScaffold, we just kick-start your project and
   take care of the boilerplate.
   However, we do include some build-time dependencies that make your life easier, such as `setuptools_scm`_.
   But don't worry, if you distribute your project in the recommended `wheel format`_ those dependencies will not affect
   the final users, they are just required during development to assembling the package file.

   That means if someone clones your repository and tries to build it, the dependencies in ``pyproject.toml``
   will be automatically pulled. This mechanism is described by `PEP 517`_/`PEP 518`_ and definitely beyond the scope of this answer.

|

3. **Why does PyScaffold ≥ 3 have a** ``src`` **folder which holds the actual Python package?**

   This avoids quite many problems compared to the case when the actual Python package resides in the same folder as
   ``setup.py``. A nice `blog post by Ionel`_ gives a thorough explanation why this is so. In a nutshell, the most severe
   problem comes from the fact that Python imports a package by first looking at the current working directory and then
   into the ``PYTHONPATH`` environment variable. If your current working directory is the root of your project directory
   you are thus not testing the installation of your package but the local package directly. Eventually, this always
   leads to huge confusion (*"But the unit tests ran perfectly on my machine!"*).

|

4. **Can I use PyScaffold ≥ 3 to develop a Python package that is Python 2 & 3 compatible?**

   Python 2 reached *end-of-life* in 2020, which means that no security updates will be available, and therefore any
   software running on Python 2 is potentially vulnerable. PyScaffold strongly recommends all packages to be ported to
   the latest supported version of Python.

   That being said, Python 3 is actually only needed for the ``putup`` command and whenever you use ``setup.py``. This means that with
   PyScaffold ≥ 3 you have to use Python 3 during the development of your package for practical reasons. If you develop
   the package using six_ you can still make it Python 2 & 3 compatible by creating a *universal* ``bdist_wheel`` package.
   This package can then be installed and run from Python 2 and 3. Just have in mind that no support for Python 2 will be provided.

|

5. **How can I get rid of PyScaffold when my project was set up using it?**


   First of all, I would really love to understand **why** you want to remove it and **what** you don't like about it.
   You can create an issue for that or just text me on `Twitter`_.
   But the good news is that your project is completely independent of PyScaffold, even if you uninstall it, everything
   will be fine.

   If you still want to remove `setuptools_scm`_ (a build-time dependency we add by default), it's actually really simple:
   Within ``setup.py`` just remove the ``use_scm_version`` argument from the ``setup()`` call which will deactivate
   the automatic version discovery. In practice, following things will **no** longer work:

   * ``python setup.py --version`` and the dynamic versioning according to the git tags when creating distributions,
     just put e.g. ``version = 0.1`` in the ``metadata`` section of ``setup.cfg`` instead,

   That's already everything you gonna lose. Not that much. You will still benefit from:

   * the smart project layout,
   * the declarative configuration with ``setup.cfg`` which comes from ``setuptools``,
   * some sane defaults in Sphinx' ``conf.py``,
   * ``.gitignore`` with some nice defaults and other dot files depending on the flags used when running ``putup``,
   * some sane defaults for pytest.

   For further cleanups, feel free to remove the dependencies from the ``requires`` key in ``pyproject.toml`` as well as
   the complete ``[pyscaffold]`` section in ``setup.cfg``.

|

6. **Can I modify** ``requires`` **despite the warning in** ``pyproject.toml`` **to avoid doing that?**

   You can definitely modify ``pyproject.toml``, but it is good to understand how PyScaffold uses it.
   If you are just adding a new build dependency (e.g. `Cython`_), there is nothing to worry.
   However, if you are trying to remove or change the version of a dependency PyScaffold included there,
   PyScaffold will overwrite that change if you ever run ``putup --update`` in the same project
   (in those cases ``git diff`` is your friend, and you should be able to manually reconcile the dependencies).

|

7. **What should I do if I am not using** ``pyproject.toml``?

   If you prefer to have legacy builds, you can remove the ``pyproject.toml`` file and run
   ``python setup.py bdist_wheel``, but we advise to install the build requirements (as the ones specified in the
   ``requires`` field of ``pyproject.toml``) in an `isolated environment`_ and use it to run the ``setup.py`` commands
   (`tox`_ can be really useful for that). Alternatively you can use the ``setup_requires`` field in `setup.cfg`_,
   however, this method is discouraged and might be invalid in the future. To skip the generation of the
   ``pyproject.toml`` file you can run ``putup`` with the ``--no-pyproject`` flag.

|

.. _blog post by Ionel: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _new issue: https://github.com/pyscaffold/pyscaffold/issues/new
.. _egg file: http://setuptools.readthedocs.io/en/latest/formats.html#eggs-and-their-formats
.. _wheel format: https://pythonwheels.com/
.. _Cargo: https://crates.io/
.. _Rust: https://www.rust-lang.org/
.. _Zen of Python: https://www.python.org/dev/peps/pep-0020/
.. _six: https://six.readthedocs.io/
.. _Twitter: https://twitter.com/FlorianWilhelm
.. _setuptools_scm: https://pypi.org/project/setuptools-scm/
.. _Cython: https://cython.org
.. _PEP 517: https://www.python.org/dev/peps/pep-0517/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _isolated environment: https://realpython.com/python-virtual-environments-a-primer/
.. _setup.cfg: https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _tox: https://tox.readthedocs.org/
