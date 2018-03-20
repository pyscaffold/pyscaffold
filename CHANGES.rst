=============
Release Notes
=============

Version 2.5.9, 2018-03-20
=========================

- Updated setuptools_scm to version v1.16.1
- Fix error with setuptools version 39.0 and above, issue #148

Version 2.5.8, 2017-09-10
=========================

- Use `sphinx.ext.imgmath` instead of `sphinx.ext.mathjax`
- Added `--with-gitlab-ci` flag for GitLab CI support
- Fix Travis install template dirties git repo, issue #107
- Updated setuptools_scm to version 1.15.6
- Updated pbr to version 3.1.1

Version 2.5.7, 2016-10-11
=========================

- Added encoding to __init__.py
- Few doc corrections in setup.cfg
- [tool:pytest] instead of [pytest] in setup.cfg
- Updated skeleton
- Switch to Google Sphinx style
- Updated setuptools_scm to version 1.13.1
- Updated pbr to version 1.10.0

Version 2.5.6, 2016-05-01
=========================

- Prefix error message with ERROR:
- Suffix of untagged commits changed from {version}-{hash} to {version}-n{hash}
- Check if package identifier is valid
- Added log level command line flags to the skeleton
- Updated pbr to version 1.9.1
- Updated setuptools_scm to version 1.11.0

Version 2.5.5, 2016-02-26
=========================

- Updated pbr to master at 2016-01-20
- Fix sdist installation bug when no git is installed, issue #90

Version 2.5.4, 2016-02-10
=========================

- Fix problem with ``fibonacci`` terminal example
- Update setuptools_scm to v1.10.1

Version 2.5.3, 2016-01-16
=========================

- Fix classifier metadata (``classifiers`` to ``classifier`` in ``setup.cfg``)

Version 2.5.2, 2016-01-02
=========================

- Fix ``is_git_installed``

Version 2.5.1, 2016-01-01
=========================

- Fix: Do some sanity checks first before gathering default options
- Updated setuptools_scm to version 1.10.0

Version 2.5, 2015-12-09
=======================

- Usage of ``test-requirements.txt`` instead of ``tests_require`` in
  ``setup.py``, issue #71
- Removed ``--with-numpydoc`` flag since this is now included by default with
  ``sphinx.ext.napoleon`` in Sphinx 1.3 and above
- Added small template for unittest
- Fix for the example skeleton file when using namespace packages
- Fix typo in devpi:upload section, issue #82
- Include ``pbr`` and ``setuptools_scm`` in PyScaffold to avoid dependency
  problems, issue #71 and #72
- Cool logo was designed by Eva Schmücker, issue #66

Version 2.4.4, 2015-10-29
=========================

- Fix problem with bad upload of version 2.4.3 to PyPI, issue #80

Version 2.4.3, 2015-10-27
=========================

- Fix problem with version numbering if setup.py is not in the root directory, issue #76

Version 2.4.2, 2015-09-16
=========================

- Fix version conflicts due to too tight pinning, issue #69

Version 2.4.1, 2015-09-09
=========================

- Fix installation with additional requirements ``pyscaffold[ALL]``
- Updated pbr version to 1.7

Version 2.4, 2015-09-02
=======================

- Allow different py.test options when invoking with ``py.test`` or
  ``python setup.py test``
- Check if Sphinx is needed and add it to *setup_requires*
- Updated pre-commit plugins
- Replaced pytest-runner by an improved version
- Let pbr do ``sphinx-apidoc``, removed from ``conf.py``, issue #65

.. note::

    Due to the switch to a modified pytest-runner version it is necessary
    to update ``setup.cfg``. Please check the :ref:`example <configuration>`.

Version 2.3, 2015-08-26
=======================

- Format of setup.cfg changed due to usage of pbr, issue #59
- Much cleaner setup.py due to usage of pbr, issue #59
- PyScaffold can be easily called from another script, issue #58
- Internally dictionaries instead of namespace objects are used for options, issue #57
- Added a section for devpi in setup.cfg, issue #62

.. note::

    Due to the switch to `pbr <http://docs.openstack.org/developer/pbr/>`_, it
    is necessary to update ``setup.cfg`` according to the new syntax.

Version 2.2.1, 2015-06-18
=========================

- FIX: Removed putup console script in setup.cfg template

Version 2.2, 2015-06-01
=======================

- Allow recursive inclusion of data files in setup.cfg, issue #49
- Replaced hand-written PyTest runner by `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`_, issue #47
- Improved default README.rst, issue #51
- Use tests/conftest.py instead of tests/__init__.py, issue #52
- Use setuptools_scm for versioning, issue #43
- Require setuptools>=9.0, issue #56
- Do not create skeleton.py during an update, issue #55

.. note::

    Due to the switch to *setuptools_scm* the following changes apply:

    - use ``python setup.py --version`` instead of ``python setup.py version``
    - ``git archive`` can no longer be used for packaging (and was never meant for it anyway)
    - initial tag ``v0.0`` is no longer necessary and thus not created in new projects
    - tags do no longer need to start with *v*

Version 2.1, 2015-04-16
=======================

- Use alabaster as default Sphinx theme
- Parameter data_files is now a section in setup.cfg
- Allow definition of extras_require in setup.cfg
- Added a CHANGES.rst file for logging changes
- Added support for cookiecutter
- FIX: Handle an empty Git repository if necessary

Version 2.0.4, 2015-03-17
=========================

- Typo and wrong Sphinx usage in the RTD documentation

Version 2.0.3, 2015-03-17
=========================

- FIX: Removed misleading `include_package_data` option in setup.cfg
- Allow selection of a proprietary license
- Updated some documentations
- Added -U as short parameter for --update

Version 2.0.2, 2015-03-04
=========================

- FIX: Version retrieval with setup.py install
- argparse example for version retrieval in skeleton.py
- FIX: import my_package should be quiet (verbose=False)

Version 2.0.1, 2015-02-27
=========================

- FIX: Installation bug under Windows 7

Version 2.0, 2015-02-25
=======================

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
=======================

- Added numpydoc flag --with-numpydoc
- Fix: Add django to requirements if --with-django
- Fix: Don't overwrite index.rst during update

Version 1.3.2, 2014-12-02
=========================

- Fix: path of Travis install script

Version 1.3.1, 2014-11-24
=========================

- Fix: --with-tox tuple bug #28

Version 1.3, 2014-11-17
=======================

- Support for Tox (https://tox.readthedocs.org/)
- flake8: exclude some files
- Usage of UTF8 as file encoding
- Fix: create non-existent files during update
- Fix: unit tests on MacOS
- Fix: unit tests on Windows
- Fix: Correct version when doing setup.py install

Version 1.2, 2014-10-13
=======================

- Support pre-commit hooks (http://pre-commit.com/)

Version 1.1, 2014-09-29
=======================

- Changed COPYING to LICENSE
- Support for all licenses from http://choosealicense.com/
- Fix: Allow update of license again
- Update to Versioneer 0.12

Version 1.0, 2014-09-05
=======================

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
=======================

- Documentation updates due to RTD
- Added a --force flag
- Some cleanups in setup.py

Version 0.8, 2014-07-25
=======================

- Update to Versioneer 0.10
- Moved sphinx-apidoc from setup.py to conf.py
- Better support for `make html`

Version 0.7, 2014-06-05
=======================

- Added Python 3.4 tests and support
- Flag --update updates only some files now
- Usage of setup_requires instead of six code

Version 0.6.1, 2014-05-15
=========================

- Fix: Removed six dependency in setup.py

Version 0.6, 2014-05-14
=======================

- Better usage of six
- Return non-zero exit status when doctests fail
- Updated README
- Fixes in Sphinx Makefile

Version 0.5, 2014-05-02
=======================

- Simplified some Travis tests
- Nicer output in case of errors
- Updated PyScaffold's own setup.py
- Added --junit_xml and --coverage_xml/html option
- Updated .gitignore file

Version 0.4.1, 2014-04-27
=========================

- Problem fixed with pytest-cov installation

Version 0.4, 2014-04-23
=======================

- PEP8 and PyFlakes fixes
- Added --version flag
- Small fixes and cleanups

Version 0.3, 2014-04-18
=======================

- PEP8 fixes
- More documentation
- Added update feature
- Fixes in setup.py

Version 0.2, 2014-04-15
=======================

- Checks when creating the project
- Fixes in COPYING
- Usage of sh instead of GitPython
- PEP8 fixes
- Python 3 compatibility
- Coverage with Coverall.io
- Some more unittests

Version 0.1.2, 2014-04-10
=========================

- Bugfix in Manifest.in
- Python 2.6 problems fixed

Version 0.1.1, 2014-04-10
=========================

- Unittesting with Travis
- Switch to string.Template
- Minor bugfixes

Version 0.1, 2014-04-03
=======================

- First release
