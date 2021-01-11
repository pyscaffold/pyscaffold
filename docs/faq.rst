.. _faq:

==========================
Frequently Asked Questions
==========================

In case you have a general question that is not answered here, please have a
look at our discussions_ and consider submitting a new one for the `Q&A`_.


Pyscaffold Usage
----------------

Does my project depend on PyScaffold when I use it to set my project up?
   Starting from version 4, your package is completely independent from PyScaffold, we just kick-start your project and
   take care of the boilerplate.
   However, we do include some build-time dependencies that make your life easier, such as `setuptools_scm`_.
   But don't worry, if you distribute your project in the recommended `wheel format`_ those dependencies will not affect
   the final users, they are just required during development to assembling the package file.

   That means if someone clones your repository and tries to build it, the dependencies in ``pyproject.toml``
   will be automatically pulled. This mechanism is described by `PEP 517`_/`PEP 518`_ and definitely beyond the scope of this answer.

Can I use PyScaffold ≥ 3 to develop a Python package that is Python 2 & 3 compatible?
   Python 2 reached *end-of-life* in 2020, which means that no security updates will be available, and therefore any
   software running on Python 2 is potentially vulnerable. PyScaffold strongly recommends all packages to be ported to
   the latest supported version of Python.

   That being said, Python 3 is actually only needed for the ``putup`` command and whenever you use ``setup.py``. This means that with
   PyScaffold ≥ 3 you have to use Python 3 during the development of your package for practical reasons. If you develop
   the package using six_ you can still make it Python 2 & 3 compatible by creating a *universal* ``bdist_wheel`` package.
   This package can then be installed and run from Python 2 and 3. Just have in mind that no support for Python 2 will be provided.

.. _remove-pyscaffold:

How can I get rid of PyScaffold when my project was set up using it?
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

Why would I use PyScaffold instead of Cookiecutter?
   PyScaffold is focused on a good out-of-the-box experience for developing distributable Python packages (exclusively).
   The idea is to standardize the structure of Python packages. Thus, PyScaffold sticks to

       "There should be one-- and preferably only one --obvious way to do it."

   from the `Zen of Python`_. The long-term goal is that PyScaffold becomes for Python what `Cargo`_ is for `Rust`_.
   Still, with the help of PyScaffold's :ref:`extension system <extensions>` customizing a project scaffold is possible.

   Cookiecutter on the other hand is a really flexible templating tool that allows you to define own templates according
   to your needs. Although some standard templates are provided that will give you quite similar results as PyScaffold,
   the overall goal of the project is quite different.

   Still, if you so desire, PyScaffold allows users to augment PyScaffold projects with certain types of cookiecutter
   templates, through its `pyscaffoldext-cookiecutter`_ extension.


File Organisation and Directory Structure
-----------------------------------------

Why does PyScaffold ≥ 3 have a ``src`` folder which holds the actual Python package?
   This avoids quite many problems compared to the case when the actual Python package resides in the same folder as
   ``setup.py``. A nice `blog post by Ionel`_ gives a thorough explanation why this is so. In a nutshell, the most severe
   problem comes from the fact that Python imports a package by first looking at the current working directory and then
   into the ``PYTHONPATH`` environment variable. If your current working directory is the root of your project directory
   you are thus not testing the installation of your package but the local package directly. Eventually, this always
   leads to huge confusion (*"But the unit tests ran perfectly on my machine!"*).

   Moreover, having a dedicated ``src`` directory to store the package files, makes it easy to comply with recent standards
   in the Python community (for example `PEP 420`_).

   Please notice that PyScaffold assumes all the files inside ``src`` are meant to be part of the package.

Can I have other files inside the ``src`` folder that are not meant for distribution?
   PyScaffold considers the ``src`` directory to be exclusively dedicated to
   store files meant to be distributed, and relies on this assumption to
   generate configuration for the several aspects of your project. Therefore
   it is not recommended to include any file not meant to distribution inside
   the ``src`` folder. (Temporary files and directories automatically
   generated by ``setuptools`` might appear from times to times though).

Where should I put extra files not meant for distribution?
   You can use the ``docs`` folder (if applicable) or create another dedicated
   folder in the root of your repository (e.g. ``examples``). The additional
   project structure created by the `pyscaffoldext-dsproject`_ is a good
   example on how to use extra folders to achieve good project organisation.


Namespaces
----------

.. _remove_implicit_namespaces:

How can I get rid of the implicit namespaces (`PEP 420`_)?
    PyScaffold uses ``setup.cfg`` to ensure `setuptools`_ will follow `PEP 420`_.
    If this configuration particularly messes up with your package, or
    you simply want to follow the old behavior, please replace
    ``packages = find_namespace:`` with ``packages = find:`` in the ``[options]``
    section of that file.

    You should also remove the ``--implicit-namespaces`` option in the
    ``cmd_line_template`` variable in the ``docs/conf.py`` file.

    Finally, if want to keep a namespace but use an explicit implementation (old
    behavior), make sure to have a look on the `packaging namespace packages
    official guide`_.  If there are already other projects with packages
    registered in the same namespace, chances are you just need to copy from
    them a sample of the ``__init__.py`` file for the umbrella folder working as
    namespace.

My namespaced package and/or other packages that use the same namespace broke after updating to PyScaffold 4. How can I fix this?
    That is likely to be happening because PyScaffold 4 removed support for
    `pkg_resources`_ namespaces in favour of `PEP 420`_. Unfortunately these two
    methodologies for creating namespaces are not compatible, as documented in
    the `packaging namespace packages official guide`_. To fix this problem you
    (or other maintainers) will need to either **(a)** update all the existing
    "subpackages" in the same namespace to be implicit (`PEP 420`_-style), or
    **(b)** get rid of the implicit namespace configuration PyScaffold
    automatically sets up during project creation/update. Please check the
    answers for :ref:`question 8 <remove_implicit_namespaces>` and :ref:`question
    10 <add_implicit_namespaces>` and the :ref:`updating <updating>` guides for some
    tips on how to achieve that.

.. _add_implicit_namespaces:

How can I convert an existing package to use implicit namespaces (`PEP 420`_)?
    The easiest answer for that question is to **(a)** convert the existing
    package to a PyScaffold-enabled project (*if it isn't yet*; please check
    :ref:`our guides <migration>` for instructions) and **(b)** :ref:`update
    <updating>` your existing project to the latest version of PyScaffold
    passing the correct ``--namespace`` option.

    The slightly more difficult answer for that question is to **(a)** make sure
    your project uses a `src layout`_, **(b)** remove the ``__init__.py`` file
    from the umbrella folder that is serving as namespace for your project,
    **(c)** configure ``setup.cfg`` to include your namespace -- have a look on
    `setuptools`_, for packages that use the ``src-layout`` that basically means
    that you want to have something similar to::

      [options]
      # ...
      packages = find_namespace:
      package_dir =
          =src
      # ...

      [options.packages.find]
      where = src

    in your ``setup.cfg`` -- and finally, **(d)** configure your documentation
    to include the implicit namespace (for `Sphinx`_ users, in general that will
    mean that you want to run ``sphinx-apidoc`` with the
    ``--implicit-namespaces`` flag after extending the ``PYTHONPATH`` with the
    ``src`` folder).

    The previous steps assume your existing package uses `setuptools`_ and you
    are willing to have a `src layout`_, if that is not the case refer to the
    documentation of your package creator (or the software you use to package
    up your Python projects) and the `PEP 420`_ for more information.


pyproject.toml
--------------

Can I modify ``requires`` despite the warning in ``pyproject.toml`` to avoid doing that?
    You can definitely modify ``pyproject.toml``, but it is good to understand how PyScaffold uses it.
    If you are just adding a new build dependency (e.g. `Cython`_), there is nothing to worry.
    However, if you are trying to remove or change the version of a dependency PyScaffold included there,
    PyScaffold will overwrite that change if you ever run ``putup --update`` in the same project
    (in those cases ``git diff`` is your friend, and you should be able to manually reconcile the dependencies).

What should I do if I am not using ``pyproject.toml`` or if it is causing me problems?
    If you prefer to have legacy builds and get the old behavior, you can remove the ``pyproject.toml`` file and run
    ``python setup.py bdist_wheel``, but we advise to install the build requirements (as the ones specified in the
    ``requires`` field of ``pyproject.toml``) in an `isolated environment`_ and use it to run the ``setup.py`` commands
    (`tox`_ can be really useful for that). Alternatively you can use the ``setup_requires`` field in `setup.cfg`_,
    however, this method is discouraged and might be invalid in the future.

    .. note::
       For the time being you can use the **transitional** ``--no-pyproject``
       option, when running ``putup``, but have in mind that this option will
       be removed in future versions of PyScaffold.

    Please check our :ref:`updating guide <updating>` for :ref:`extra steps <no-pyproject-steps>`
    you might need to execute manually.

.. _version-faq:

Best Practices and Common Errors with Version Numbers
-----------------------------------------------------

How do I get a clean version like 3.2.4 when I have 3.2.3.post0.dev9+g6817bd7?
    Just commit all your changes and create a new tag using ``git tag v3.2.4``.
    In order to build an old version checkout an old tag, e.g. ``git checkout -b v3.2.3 v3.2.3``
    and run ``tox -e build`` or ``python setup.py bdist_wheel``.

Why do I see `unknown` as version?
    In most cases this happens if your source code is no longer a proper Git repository, maybe because
    you moved or copied it or Git is not even installed. In general using ``pip install -e .``,
    ``python setup.py install`` or ``python setup.py develop`` to install your package is only recommended
    for developers of your Python project, which have Git installed and use a proper Git repository anyway.
    Users of your project should always install it using the distribution you built for them e.g.
    ``pip install my_project-3.2.3-py3-none-any.whl``.  You build such a distribution by running
    ``tox -e build`` (or ``python setup.py bdist_wheel``) and then find it under ``./dist``.

Is there a good versioning scheme I should follow?
    The most common practice is to use `Semantic Versioning`_. Following this practice avoids the so called
    `dependency hell`_ for the users of your package. Also be sure to set attributes like ``python_requires``
    and ``install_requires`` appropriately in ``setup.cfg``.

Is there a best practice for distributing my package?
    First of all, cloning your repository or just coping your code around is a really bad practice which comes
    with tons of pitfalls. The *clean* way is to first build a distribution and then give this distribution to
    your users. This can be done by just copying the distribution file or uploading it to some artifact store
    like `PyPI`_ for public packages or `devpi`_, `Nexus`_, etc. for private packages. Also check out this
    article about `packaging, versioning and continuous integration`_.

Using some CI service, why is the version `unknown` or `my_project-0.0.post0.dev50`?
    Some CI services use shallow git clones, i.e. ``--depth N``, or don't download git tags to save bandwidth.
    To verify that your repo works as expected, run::

        git describe --dirty --tags --long --first-parent

    which is basically what `setuptools_scm`_ does to retrieve the correct version number. If this command
    fails, tweak how your repo is cloned depending on your CI service and make sure to also download the tags,
    i.e. ``git fetch origin --tags``.


.. _blog post by Ionel: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _src layout: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _discussions: https://github.com/pyscaffold/pyscaffold/discussions
.. _Q&A: https://github.com/pyscaffold/pyscaffold/discussions/categories/q-a
.. _egg file: http://setuptools.readthedocs.io/en/latest/formats.html#eggs-and-their-formats
.. _wheel format: https://pythonwheels.com/
.. _Cargo: https://crates.io/
.. _Rust: https://www.rust-lang.org/
.. _Zen of Python: https://www.python.org/dev/peps/pep-0020/
.. _six: https://six.readthedocs.io/
.. _Twitter: https://twitter.com/FlorianWilhelm
.. _setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html#options
.. _setuptools_scm: https://pypi.org/project/setuptools-scm/
.. _Cython: https://cython.org
.. _PEP 517: https://www.python.org/dev/peps/pep-0517/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _PEP 420: https://www.python.org/dev/peps/pep-0420/
.. _isolated environment: https://realpython.com/python-virtual-environments-a-primer/
.. _setup.cfg: https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
.. _tox: https://tox.readthedocs.org/
.. _packaging namespace packages official guide: https://packaging.python.org/guides/packaging-namespace-packages/
.. _pkg_resources: https://setuptools.readthedocs.io/en/latest/pkg_resources.html
.. _Sphinx: http://www.sphinx-doc.org/
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _Semantic Versioning: https://semver.org/
.. _dependency hell: https://en.wikipedia.org/wiki/Dependency_hell
.. _PyPI: https://pypi.org/
.. _devpi: https://devpi.net/
.. _Nexus: https://www.sonatype.com/product-nexus-repository
.. _packaging, versioning and continuous integration: https://florianwilhelm.info/2018/01/ds_in_prod_packaging_ci/
