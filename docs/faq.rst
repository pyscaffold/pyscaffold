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
   However, we do include some build-time dependencies that make your life easier, such as :pypi:`setuptools-scm`.
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

   If you still want to remove :pypi:`setuptools-scm` (a build-time dependency we add by default), it's actually really simple:

   * Within ``setup.py`` remove the ``use_scm_version`` argument from the ``setup()``
   * Remove the ``[tool.setuptools_scm]`` section of ``pyproject.toml``.

   This will deactivate the automatic version discovery. In practice, following things will **no** longer work:

   * ``python setup.py --version`` and the dynamic versioning according to the git tags when creating distributions,
     just put e.g. ``version = 0.1`` in the ``metadata`` section of ``setup.cfg`` instead,

   That's already everything you gonna lose. Not that much. You will still benefit from:

   * the smart project layout,
   * the declarative configuration with ``setup.cfg`` which comes from `setuptools`_,
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

.. _python-api:

How can I embed PyScaffold into another application?
    PyScaffold is expected to be used from terminal, via ``putup`` command line
    application. It is, however, possible to write an external script or program
    that embeds PyScaffold and use it to perform some custom actions.

    The public Python API for embedding PyScaffold is composed by the main function
    :obj:`pyscaffold.api.create_project` in addition to :obj:`pyscaffold.api.NO_CONFIG`,
    :obj:`pyscaffold.log.DEFAULT_LOGGER`, :obj:`pyscaffold.log.logger` (partially,
    see details bellow), and the constructors for the extension classes belonging
    to the :mod:`pyscaffold.extenstions` module (the other methods and functions
    are not considered part of the API). This API, as explicitly listed, follows
    `Semantic Versioning`_ and will not change in a backwards incompatible way
    between releases. The remaining methods and functions are not guaranteed to be stable.

    The following example illustrates a typical embedded usage of PyScaffold:

    .. code-block:: python

        import logging

        from pyscaffold.api import create_project
        from pyscaffold.extenstions.cirrus import Cirrus
        from pyscaffold.extenstions.namespace import Namespace
        from pyscaffold.log import DEFAULT_LOGGER as LOGGER_NAME

        logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)

        create_project(
            project_path="my-proj-name",
            author="Your Name",
            namespace="some.namespace",
            license="MIT",
            extensions=[Cirrus(), Namespace()],
        )

    Note that no built-in extension (e.g. **cirrus** and **namespace**)
    is activated by default. The ``extensions`` option should be manually
    populated when convenient.

    PyScaffold uses the logging infrastructure from Python standard library, and
    emits notifications during its execution. Therefore, it is possible to control
    which messages are logged by properly setting the log level (internally, most
    of the messages are produced under the ``INFO`` level).  By default, a
    :class:`~logging.StreamHandler` is attached to the logger, however it is
    possible to replace it with a custom handler using
    :obj:`logging.Logger.removeHandler` and :obj:`logging.Logger.addHandler`. The
    logger object is available under the :obj:`~pyscaffold.log.logger` variable of
    the :mod:`pyscaffold.log` module. The default handler is available under the
    :obj:`~pyscaffold.log.ReportLogger.handler` property of the
    :obj:`~pyscaffold.log.logger` object.


How can I use PyScaffold if my project is nested within a larger repository, e.g. in a monorepo?
    If you use PyScaffold to create a Python project within another larger repository, you will see
    the following error when building your package::

        LookupError: setuptools-scm was unable to detect version for '/path/to/your/project'::

    This is due to the fact that :pypi:`setuptools-scm` assumes that the root of your repository is where
    ``pyproject.toml`` resides. In order to tell :pypi:`setuptools-scm` where the actual root is
    some changes have to be made. In the example below we assume that the root of the repository is
    the parent directory of your project, i.e. ``..`` as relative path. In any case you need to specify the root of the repository
    relative to the root of your project.

    1. ``pyproject.toml``::

        [tool.setuptools_scm]
        # See configuration details in https://github.com/pypa/setuptools_scm
        version_scheme = "no-guess-dev"
        # ADD THE TWO LINES BELOW
        root = ".."
        relative_to = "setup.py"

    2. ``setup.py``::

        setup(use_scm_version={"root": "..",  # ADD THIS...
                               "relative_to": __file__,  # ... AND THAT!
                               "version_scheme": "no-guess-dev"})

    In future versions of PyScaffold this will be much simpler as ``pyproject.toml`` will completely replace ``setup.py``.


What is the license of the generated project scaffold? Is there anything I need to consider?
    The source code of PyScaffold itself is MIT-licensed with the exception of the `*.template` files under the ``pyscaffold.templates`` subpackage,
    which are licensed under the BSD 0-Clause license (0BSD). Thus, also the generated boilerplate code for your project
    is 0BSD-licensed and consequently you have no obligations at all and can do whatever you want except of suing us ;-)


Why my file is not being included in the sdist/wheel distribution?
    By default projects generated with PyScaffold rely on :pypi:`setuptools-scm` to populate the generated sdist or wheel, which in
    turn uses ``git`` to list all the *non-transient project files*.
    Therefore, if you create non-Python files, you need to **make sure they are being tracked by git** before building your project.

    You can check if a file is being tracked by running ``git ls-files`` and ``setuptools-scm``::

        $ git ls-files
        $ python -m setuptools_scm ls
        # ^-- assumes you have `setuptools-scm` installed in your environment

    Note that non-Python files depend on the ``include_package_data`` :ref:`configuration parameter <configuration>`
    being set to ``True``.
    If you want to include *transient* files in your distributions, please check `setuptools docs on data files`_.

.. _git-default-branch:

How can I change Git's default branch when creating a new project setup with PyScaffold?
    The default branch in Git used to be ``master`` (and still is at least until version 2.32) but nowadays ``main`` is a
    preferred name. When you use PyScaffold's ``putup`` to set up your project and want to explicitly set the default branch
    name, just configure this using ``git config``, e.g.::

        $ git config --global init.defaultBranch main

    In case you already created the project scaffold, you can just rename the branch, e.g. with ``git branch -m master main``.

File Organisation and Directory Structure
-----------------------------------------

Why does PyScaffold ≥ 3 have a ``src`` folder which holds the actual Python package?
   This avoids quite many problems compared to the case when the actual Python package resides in the same folder as
   your configuration and test files.
   A nice `blog post by Ionel`_ gives a thorough explanation why this is so. In a nutshell, the most severe
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

How can I fix problems with my namespace package after an upgrade to PyScaffold 4?
    That is likely to be happening because PyScaffold 4 removed support for
    `pkg_resources`_ namespaces in favour of `PEP 420`_. Unfortunately these two
    methodologies for creating namespaces are not compatible, as documented in
    the `packaging namespace packages official guide`_. To fix this problem you
    (or other maintainers) will need to either **(a)** update all the existing
    "subpackages" in the same namespace to be implicit (`PEP 420`_-style), or
    **(b)** get rid of the implicit namespace configuration PyScaffold
    automatically sets up during project creation/update. Please check the
    answers for these other questions about :ref:`removing <remove_implicit_namespaces>`
    or :ref:`adding <add_implicit_namespaces>` implicit namespaces and the
    :ref:`updating <updating>` guides for some tips on how to achieve that.

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
    and run ``tox -e build`` (or install the ``build`` package and run ``python -m build --wheel``).

Why do I see `unknown` as version?
    In most cases this happens if your source code is no longer a proper Git repository, maybe because
    you moved or copied it or Git is not even installed.
    In general using ``pip install -e .`` to install your package is only recommended
    for developers of your Python project, which have Git installed and use a proper Git repository anyway.
    Users of your project should always install it using the distribution you built for them e.g.
    ``pip install my_project-3.2.3-py3-none-any.whl``.  You build such a distribution by running
    ``tox -e build`` (or ``python -m build --wheel`` after installing ``build``) and then find it under ``./dist``.

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

    which is basically what :pypi:`setuptools-scm` does to retrieve the correct version number. If this command
    fails, tweak how your repo is cloned depending on your CI service and make sure to also download the tags,
    i.e. ``git fetch origin --tags``.

How can I build a distribution if I have only the source code without a proper git repo?
    If you see an error message like::

       setuptools-scm was unable to detect version for 'your/project'.

    This means that ``setuptools-scm`` could not find an intact git repository. If you still want to build
    a distribution from the source code there is a workaround:
    you can try setting :pypi:`setuptools-scm` environment variables, e.g. ``SETUPTOOLS_SCM_PRETEND_VERSION=1.0``.
    If that is not enough, try completely removing it. In ``setup.cfg`` in the section ``[metadata]``
    define a version manually with e.g. ``version = 1.0``. Now remove from ``pyproject.toml`` the
    ``setuptools_scm`` build requirement and the ``[tool.setuptools_scm]`` table.
    Also remove ``use_scm_version={"version_scheme": "no-guess-dev"}`` from ``setup.py``.

How can I configure and debug the exact version exported by my package?
    PyScaffold will include a default configuration for your project
    that uses the name of the latest git tag and the status of your working
    tree to create a suitable version string.

    You can tweak this configuration to change how this string is produced. The
    details on how to do this are described in :pypi:`setuptools-scm`.

    To preview (or debug) what is the version string being exported you can
    run::

        python -m setuptools_scm

    (This requires the ``setuptools-scm`` package is installed in your environment)


.. _blog post by Ionel: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _src layout: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. _discussions: https://github.com/pyscaffold/pyscaffold/discussions
.. _Q&A: https://github.com/pyscaffold/pyscaffold/discussions/categories/q-a
.. _wheel format: https://pythonwheels.com
.. _Cargo: https://doc.rust-lang.org/stable/cargo/
.. _Rust: https://www.rust-lang.org
.. _Zen of Python: https://www.python.org/dev/peps/pep-0020
.. _six: https://six.readthedocs.io
.. _Twitter: https://twitter.com/FlorianWilhelm
.. _setuptools: https://setuptools.pypa.io/en/stable/userguide/declarative_config.html
.. _setuptools docs on data files: https://setuptools.pypa.io/en/latest/userguide/datafiles.html
.. _Cython: https://cython.org
.. _PEP 517: https://www.python.org/dev/peps/pep-0517/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _PEP 420: https://www.python.org/dev/peps/pep-0420/
.. _isolated environment: https://realpython.com/python-virtual-environments-a-primer/
.. _setup.cfg: https://setuptools.pypa.io/en/stable/userguide/declarative_config.html
.. _tox: https://tox.wiki/en/stable/
.. _packaging namespace packages official guide: https://packaging.python.org/guides/packaging-namespace-packages
.. _pkg_resources: https://setuptools.pypa.io/en/stable/pkg_resources.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _pyscaffoldext-cookiecutter: https://github.com/pyscaffold/pyscaffoldext-cookiecutter
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _Semantic Versioning: https://semver.org/
.. _dependency hell: https://en.wikipedia.org/wiki/Dependency_hell
.. _devpi: https://www.devpi.net
.. _Nexus: https://www.sonatype.com/products/repository-oss
.. _packaging, versioning and continuous integration: https://florianwilhelm.info/2018/01/ds_in_prod_packaging_ci
.. _PyPI: https://pypi.org/
