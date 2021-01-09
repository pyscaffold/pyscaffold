=========
Changelog
=========

Development version
===================

Version 4.0
-----------

- Cookiecutter, Django and Travis extensions extracted to their own repositories, :issue:`175` and :issue:`355`
- Support for Python 3.4 and 3.5 dropped, :issue:`226`
- Dropped deprecated ``requirements.txt`` file, :issue:`182`
- Added support for global configuration (avoid retyping common ``putup``'s options), :issue:`236`
- PyScaffold is no longer a build-time dependency, it just generates the project structure
- Removed ``contrib`` subpackage, vendorized packages are now runtime dependencies, :pr:`290`
- ``setuptools_scm`` is included by default in ``setup.cfg``, ``setup.py`` and ``pyproject.toml``
- API changed to use ``pyscaffold.operations`` instead of integer flags, :issue:`271`
- Allow ``string.Template`` and ``callable`` as file contents in project structure, :pr:`295`
- Extract file system functions from ``utils.py`` into ``file_system.py``
- Extract identification/naming functions from ``utils.py`` into ``identification.py``
- Extract action related functions from ``api/__init__.py`` to ``actions.py``
- ``helpers.{modify,ensure,reject}`` moved to ``structure.py``
- ``helpers.{register,unregister}`` moved to ``actions.py``
- New extension for automatically creating virtual environments (``--venv``)
- Added instructions to use ``pip-tools`` to docs
- ``pre-commit`` extension now attempts to install hooks automatically
- A nice message is now displayed when PyScaffold finishes running (``actions.report_done``)
- Removed mutually exclusive argparse groups for extensions, :pr:`315`
- Progressive type annotations adopted in the code base together with mypy linting
- Simplified isort config
- ``pyproject.toml`` and isolated builds adopted by default, :issue:`256`
- Added comment to ``setup.cfg`` template instructing about extra links, :issue:`268`
- Generate ``tox.ini`` by default, :issue:`296`
- Replace ``pkg_resources`` with ``importlib.{metadata,resources}`` and ``packaging``, :issue:`309`
- Adopt PEP 420 for namespaces, :issue:`218`
- Adopt SPDX identifiers for the license field in ``setup.cfg``, :issue:`319`
- Removed deprecated ``log.configure_logger``
- Add links to issues and pull requests to changelog, :pr:`363`
- Add an experimental ``--interactive`` *mode* (inspired by ``git rebase -i``), :issue:`191`
  (additional discussion: :pr:`333`, :pr:`325`, :pr:`362`)
- Reorganise the **FAQ** (including version questions previously in **Features**)
- Updated ``setuptools`` and ``setuptools_scm`` dependencies to minimal versions 46.1 and 5, respectively
- Adopted ``no-guess-dev`` version scheme from ``setuptools_scm`` (semantically all stays the same, but
  non-tag commits are now versioned ``LAST_TAG.post1.devN`` instead of ``LAST_TAG.post0.devN``)
- Fix problem of not showing detailed log with ``--verbose`` if error happens when loading extensions :issue:`378`

Current versions
================

Version 3.3, 2020-12-24
-----------------------

- Code base changed to Black's standards
- New docs about version numbers and git integration
- Updated pre-commit hooks
- Updated ``docs/Makefile`` to use Sphinx "make mode"
- *deprecated* setuptools extensions/commands ``python setup.py test/docs/doctests``, :issue:`245`
- New tox test environments for generating docs and running doctests
- New built-in extension for Cirrus CI, :issue:`251`
- *experimental* ``get_template`` is now part of the public API and can be used by extensions, :issue:`252`
- Updated ``setuptools_scm`` to version 4.1.2 in contrib
- Updated ``configupdater`` to version 1.1.2 in contrib
- precommit automatically fixes line endings by default
- *deprecated* ``log.configure_logger``, use ``log.logger.reconfigure`` instead

.. note::

    PyScaffold 3.3 is the last release to support Python 3.5

Version 3.2.3, 2019-10-12
-------------------------

- Updated ``configupdater`` to version 1.0.1
- Changed Travis to Cirrus CI
- Fix some problems with Windows


Older versions
==============

Version 3.2.2, 2019-09-12
-------------------------

- Write files as UTF-8, fixes ``codec can't encode characters`` error

Version 3.2.1, 2019-07-11
-------------------------

- Updated pre-commit configuration and set max-line-length to 88 (Black's default)
- Change build folder of Sphinx's Makefile
- Fix creation of empty files which were just ignored before

Version 3.2, 2019-06-30
-----------------------

- *deprecated* use of lists with ``helpers.{modify,ensure,reject}``, :issue:`211`
- Add support for ``os.PathLike`` objects in ``helpers.{modify,ensure,reject}``, :issue:`211`
- Remove ``release`` alias in ``setup.cfg``, use ``twine`` instead
- Set ``project-urls`` and ``long-description-content-type`` in ``setup.cfg``, :issue:`216`
- Added additional command line argument ``very-verbose``
- Assure clean workspace when updating existing project, :issue:`190`
- Show stacktrace on errors if ``--very-verbose`` is used
- Updated ``configupdater`` to version 1.0
- Use ``pkg_resources.resource_string`` instead of ``pkgutil.get_data`` for templates
- Update ``setuptools_scm`` to version 3.3.3
- Updated pytest-runner to version 5.1
- Some fixes regarding the order of executing extensions
- Consider ``GIT_AUTHOR_NAME`` and ``GIT_AUTHOR_EMAIL`` environment variables
- Updated ``tox.ini``
- Switch to using tox in ``.travis.yml`` template
- Reworked all official extensions ``--pyproject``, ``--custom-extension`` and ``--markdown``

Version 3.1, 2018-09-05
-----------------------

- Officially dropped Python 2 support, :issue:`177`
- Moved ``entry_points`` and ``setup_requires`` to ``setup.cfg``, :issue:`176`
- Updated ``travis.yml`` template, :issue:`181`
- Set ``install_requires`` to setuptools>=31
- Better isolation of unit tests, :issue:`119`
- Updated tox template, issues :issue:`160` & :issue:`161`
- Use ``pkg_resources.parse_version`` instead of old ``LooseVersion`` for parsing
- Use ``ConfigUpdater`` instead of ``ConfigParser``
- Lots of internal cleanups and improvements
- Updated pytest-runner to version 4.2
- Updated setuptools_scm to version 3.1
- Fix Django extension problem with src-layout, :issue:`196`
- *experimental* extension for MarkDown usage in README, :issue:`163`
- *experimental* support for Pipenv, :issue:`140`
- *deprecated* built-in Cookiecutter and Django extensions (to be moved to separated packages), :issue:`175`

Version 2.5.11, 2018-04-14
--------------------------

- Updated pbr to version 4.0.2
- Fixes Sphinx version 1.6 regression, :issue:`152`

Version 3.0.3, 2018-04-14
-------------------------

- Set install_requires to setuptools>=30.3.0

Version 3.0.2, 2018-03-21
-------------------------

- Updated setuptools_scm to version 1.17.0
- Fix wrong docstring in skeleton.py about entry_points, :issue:`147`
- Fix error with setuptools version 39.0 and above, :issue:`148`
- Fixes in documentation, thanks Vicky

Version 2.5.10, 2018-03-21
--------------------------

- Updated setuptools_scm to version 1.17.0

Version 2.5.9, 2018-03-20
-------------------------

- Updated setuptools_scm to version 1.16.1
- Fix error with setuptools version 39.0 and above, :issue:`148`

Version 3.0.1, 2018-02-13
-------------------------

- Fix confusing error message when ``python setup.py docs`` and Sphinx is not installed, :issue:`142`
- Fix 'unknown' version in case project name differs from the package name, :issue:`141`
- Fix missing ``file:`` attribute in long-description of setup.cfg
- Fix ``sphinx-apidoc`` invocation problem with Sphinx 1.7

Version 3.0, 2018-01-07
-----------------------

- Improved Python API thanks to an extension system
- Dropped pbr in favor of setuptools >= 30.3.0
- Updated setuptools_scm to v1.15.6
- Changed ``my_project/my_package`` to recommended ``my_project/src/my_package`` structure
- Renamed ``CHANGES.rst`` to more standard ``CHANGELOG.rst``
- Added platforms parameter in ``setup.cfg``
- Call Sphinx api-doc from ``conf.py``, :issue:`98`
- Included six 1.11.0 as contrib sub-package
- Added ``CONTRIBUTING.rst``
- Removed ``test-requirements.txt`` from template
- Added support for GitLab
- License change from New BSD to MIT
- FIX: Support of git submodules, :issue:`98`
- Support of Cython extensions, :issue:`48`
- Removed redundant ``--with-`` from most command line flags
- Prefix ``n`` was removed from the local_version string of dirty versions
- Added a ``--pretend`` flag for easier development of extensions
- Added a ``--verbose`` flag for more output what PyScaffold is doing
- Use pytest-runner 4.4 as contrib package
- Added a ``--no-skeleton`` flag to omit the creation of ``skeleton.py``
- Save parameters used to create project scaffold in ``setup.cfg`` for later updating

A special thanks goes to Anderson Bravalheri for his awesome support
and `inovex <https://www.inovex.de/en/>`_ for sponsoring this release.

Version 2.5.8, 2017-09-10
-------------------------

- Use ``sphinx.ext.imgmath`` instead of ``sphinx.ext.mathjax``
- Added ``--with-gitlab-ci`` flag for GitLab CI support
- Fix Travis install template dirties git repo, :issue:`107`
- Updated setuptools_scm to version 1.15.6
- Updated pbr to version 3.1.1

Version 2.5.7, 2016-10-11
-------------------------

- Added encoding to __init__.py
- Few doc corrections in setup.cfg
- [tool:pytest] instead of [pytest] in setup.cfg
- Updated skeleton
- Switch to Google Sphinx style
- Updated setuptools_scm to version 1.13.1
- Updated pbr to version 1.10.0

Version 2.5.6, 2016-05-01
-------------------------

- Prefix error message with ERROR:
- Suffix of untagged commits changed from {version}-{hash} to {version}-n{hash}
- Check if package identifier is valid
- Added log level command line flags to the skeleton
- Updated pbr to version 1.9.1
- Updated setuptools_scm to version 1.11.0

Version 2.5.5, 2016-02-26
-------------------------

- Updated pbr to master at 2016-01-20
- Fix sdist installation bug when no git is installed, :issue:`90`

Version 2.5.4, 2016-02-10
-------------------------

- Fix problem with ``fibonacci`` terminal example
- Update setuptools_scm to v1.10.1

Version 2.5.3, 2016-01-16
-------------------------

- Fix classifier metadata (``classifiers`` to ``classifier`` in ``setup.cfg``)

Version 2.5.2, 2016-01-02
-------------------------

- Fix ``is_git_installed``

Version 2.5.1, 2016-01-01
-------------------------

- Fix: Do some sanity checks first before gathering default options
- Updated setuptools_scm to version 1.10.0

Version 2.5, 2015-12-09
-----------------------

- Usage of ``test-requirements.txt`` instead of ``tests_require`` in
  ``setup.py``, :issue:`71`
- Removed ``--with-numpydoc`` flag since this is now included by default with
  ``sphinx.ext.napoleon`` in Sphinx 1.3 and above
- Added small template for unittest
- Fix for the example skeleton file when using namespace packages
- Fix typo in devpi:upload section, :issue:`82`
- Include ``pbr`` and ``setuptools_scm`` in PyScaffold to avoid dependency
  problems, :issue:`71` and :issue:`72`
- Cool logo was designed by Eva Schmücker, :issue:`66`

Version 2.4.4, 2015-10-29
-------------------------

- Fix problem with bad upload of version 2.4.3 to PyPI, :issue:`80`

Version 2.4.3, 2015-10-27
-------------------------

- Fix problem with version numbering if setup.py is not in the root directory, :issue:`76`

Version 2.4.2, 2015-09-16
-------------------------

- Fix version conflicts due to too tight pinning, :issue:`69`

Version 2.4.1, 2015-09-09
-------------------------

- Fix installation with additional requirements ``pyscaffold[ALL]``
- Updated pbr version to 1.7

Version 2.4, 2015-09-02
-----------------------

- Allow different py.test options when invoking with ``py.test`` or
  ``python setup.py test``
- Check if Sphinx is needed and add it to *setup_requires*
- Updated pre-commit plugins
- Replaced pytest-runner by an improved version
- Let pbr do ``sphinx-apidoc``, removed from ``conf.py``, :issue:`65`

.. note::

    Due to the switch to a modified pytest-runner version it is necessary
    to update ``setup.cfg``. Please check the :ref:`example <configuration>`.

Version 2.3, 2015-08-26
-----------------------

- Format of setup.cfg changed due to usage of pbr, :issue:`59`
- Much cleaner setup.py due to usage of pbr, :issue:`59`
- PyScaffold can be easily called from another script, :issue:`58`
- Internally dictionaries instead of namespace objects are used for options, :issue:`57`
- Added a section for devpi in setup.cfg, :issue:`62`

.. note::

    Due to the switch to `pbr <http://docs.openstack.org/developer/pbr/>`_, it
    is necessary to update ``setup.cfg`` according to the new syntax.

Version 2.2.1, 2015-06-18
-------------------------

- FIX: Removed putup console script in setup.cfg template

Version 2.2, 2015-06-01
-----------------------

- Allow recursive inclusion of data files in setup.cfg, :issue:`49`
- Replaced hand-written PyTest runner by `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`_, :issue:`47`
- Improved default README.rst, :issue:`51`
- Use tests/conftest.py instead of tests/__init__.py, :issue:`52`
- Use setuptools_scm for versioning, :issue:`43`
- Require setuptools>=9.0, :issue:`56`
- Do not create skeleton.py during an update, :issue:`55`

.. note::

    Due to the switch to *setuptools_scm* the following changes apply:

    - use ``python setup.py --version`` instead of ``python setup.py version``
    - ``git archive`` can no longer be used for packaging (and was never meant for it anyway)
    - initial tag ``v0.0`` is no longer necessary and thus not created in new projects
    - tags do no longer need to start with *v*

Version 2.1, 2015-04-16
-----------------------

- Use alabaster as default Sphinx theme
- Parameter data_files is now a section in setup.cfg
- Allow definition of extras_require in setup.cfg
- Added a CHANGES.rst file for logging changes
- Added support for cookiecutter
- FIX: Handle an empty Git repository if necessary

Version 2.0.4, 2015-03-17
-------------------------

- Typo and wrong Sphinx usage in the RTD documentation

Version 2.0.3, 2015-03-17
-------------------------

- FIX: Removed misleading `include_package_data` option in setup.cfg
- Allow selection of a proprietary license
- Updated some documentations
- Added -U as short parameter for --update

Version 2.0.2, 2015-03-04
-------------------------

- FIX: Version retrieval with setup.py install
- argparse example for version retrieval in skeleton.py
- FIX: import my_package should be quiet (verbose=False)

Version 2.0.1, 2015-02-27
-------------------------

- FIX: Installation bug under Windows 7

Version 2.0, 2015-02-25
-----------------------

- Split configuration and logic into setup.cfg and setup.py
- Removed .pre from version string (newer PEP 440)
- FIX: Sphinx now works if package name does not equal project name
- Allow namespace packages with --with-namespace
- Added a skeleton.py as a console_script template
- Set `v0.0` as initial tag to support PEP440 version inference
- Integration of the Versioneer functionality into setup.py
- Usage of `data_files` configuration instead of `MANIFEST.in`
- Allow configuration of `package_data` in `setup.cfg`
- Link from Sphinx docs to AUTHORS.rst

Version 1.4, 2014-12-16
-----------------------

- Added numpydoc flag --with-numpydoc
- Fix: Add django to requirements if --with-django
- Fix: Don't overwrite index.rst during update

Version 1.3.2, 2014-12-02
-------------------------

- Fix: path of Travis install script

Version 1.3.1, 2014-11-24
-------------------------

- Fix: --with-tox tuple bug, :issue:`28`

Version 1.3, 2014-11-17
-----------------------

- Support for Tox (https://tox.readthedocs.org/)
- flake8: exclude some files
- Usage of UTF8 as file encoding
- Fix: create non-existent files during update
- Fix: unit tests on MacOS
- Fix: unit tests on Windows
- Fix: Correct version when doing setup.py install

Version 1.2, 2014-10-13
-----------------------

- Support pre-commit hooks (http://pre-commit.com/)

Version 1.1, 2014-09-29
-----------------------

- Changed COPYING to LICENSE
- Support for all licenses from http://choosealicense.com/
- Fix: Allow update of license again
- Update to Versioneer 0.12

Version 1.0, 2014-09-05
-----------------------

- Fix when overwritten project has a git repository
- Documentation updates
- License section in Sphinx
- Django project support with --with-django flag
- Travis project support with --with-travis flag
- Replaced sh with own implementation
- Fix: new `git describe` version to PEP440 conversion
- conf.py improvements
- Added source code documentation
- Fix: Some Python 2/3 compatibility issues
- Support for Windows
- Dropped Python 2.6 support
- Some classifier updates

Version 0.9, 2014-07-27
-----------------------

- Documentation updates due to RTD
- Added a --force flag
- Some cleanups in setup.py

Version 0.8, 2014-07-25
-----------------------

- Update to Versioneer 0.10
- Moved sphinx-apidoc from setup.py to conf.py
- Better support for `make html`

Version 0.7, 2014-06-05
-----------------------

- Added Python 3.4 tests and support
- Flag --update updates only some files now
- Usage of setup_requires instead of six code

Version 0.6.1, 2014-05-15
-------------------------

- Fix: Removed six dependency in setup.py

Version 0.6, 2014-05-14
-----------------------

- Better usage of six
- Return non-zero exit status when doctests fail
- Updated README
- Fixes in Sphinx Makefile

Version 0.5, 2014-05-02
-----------------------

- Simplified some Travis tests
- Nicer output in case of errors
- Updated PyScaffold's own setup.py
- Added --junit_xml and --coverage_xml/html option
- Updated .gitignore file

Version 0.4.1, 2014-04-27
-------------------------

- Problem fixed with pytest-cov installation

Version 0.4, 2014-04-23
-----------------------

- PEP8 and PyFlakes fixes
- Added --version flag
- Small fixes and cleanups

Version 0.3, 2014-04-18
-----------------------

- PEP8 fixes
- More documentation
- Added update feature
- Fixes in setup.py

Version 0.2, 2014-04-15
-----------------------

- Checks when creating the project
- Fixes in COPYING
- Usage of sh instead of GitPython
- PEP8 fixes
- Python 3 compatibility
- Coverage with Coverall.io
- Some more unittests

Version 0.1.2, 2014-04-10
-------------------------

- Bugfix in Manifest.in
- Python 2.6 problems fixed

Version 0.1.1, 2014-04-10
-------------------------

- Unittesting with Travis
- Switch to string.Template
- Minor bugfixes

Version 0.1, 2014-04-03
-----------------------

- First release
