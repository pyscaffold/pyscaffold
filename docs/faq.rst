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

   The short answer is no if you later distribute your project in the recommended `wheel format`_. The longer answer is
   that only during development PyScaffold is needed as a setup dependency. That means if someone clones your repository
   and runs ``setup.py``, ``setuptools`` checks for the ``setup_requires`` argument which includes PyScaffold and installs
   PyScaffold automatically as `egg file`_ into ``.eggs`` if PyScaffold is not yet installed. This mechanism is provided
   by ``setuptools`` and definitely beyond the scope of this answer. The same applies for the deprecated source
   distribution (``sdist``) but not for a binary distribution (``bdist``). Anyways, the recommend way is nowadays a binary
   wheel distribution (``bdist_wheel``) which will not depend on PyScaffold at all.

|

3. **Why does PyScaffold 3 have a** ``src`` **folder which holds the actual Python package?**

   This avoids quite many problems compared to the case when the actual Python package resides in the same folder as
   ``setup.py``. A nice `blog post by Ionel`_ gives a thorough explanation why this is so. In a nutshell, the most severe
   problem comes from the fact that Python imports a package by first looking at the current working directory and then
   into the ``PYTHONPATH`` environment variable. If your current working directory is the root of your project directory
   you are thus not testing the installation of your package but the local package directly. Eventually, this always
   leads to huge confusion (*"But the unit tests ran perfectly on my machine!"*).

|

4. **Can I use PyScaffold 3 to develop a Python package that is Python 2 & 3 compatible?**

   Python 3 is actually only needed for the ``putup`` command and whenever you use ``setup.py``. This means that with
   PyScaffold 3 you have to use Python 3 during the development of your package for practical reasons. If you develop
   the package using six_ you can still make it Python 2 & 3 compatible by creating a *universal* ``bdist_wheel`` package.
   This package can then be installed and run from Python 2 and 3.

|

.. _blog post by Ionel: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _new issue: https://github.com/pyscaffold/pyscaffold/issues/new
.. _egg file: http://setuptools.readthedocs.io/en/latest/formats.html#eggs-and-their-formats
.. _wheel format: https://pythonwheels.com/
.. _Cargo: https://crates.io/
.. _Rust: https://www.rust-lang.org/
.. _Zen of Python: https://www.python.org/dev/peps/pep-0020/
.. _six: https://six.readthedocs.io/
