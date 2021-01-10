============
Contributing
============

PyScaffold was started by `Blue Yonder`_ developers to help automating and
standardizing the process of project setups. Nowadays it is a pure community
project and you are very welcome to join in our effort if you would like
to contribute.


Issue Reports
=============

If you experience bugs or in general issues with PyScaffold, please file an
issue report on our `issue tracker`_.


Code Contributions
==================

Submit an issue
---------------

Before you work on any non-trivial code contribution it's best to first create
an issue report to start a discussion on the subject. This often provides
additional considerations and avoids unnecessary work.

Create an environment
---------------------

Before you start coding we recommend to install Miniconda_ which allows
to setup a dedicated development environment named ``pyscaffold`` with::

   conda create -n pyscaffold python=3 six virtualenv pytest pytest-cov

Then activate the environment ``pyscaffold`` with::

   source activate pyscaffold

Clone the repository
--------------------

#. `Create a Gitub account`_  if you do not already have one.
#. Fork the `project repository`_: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on the GitHub server.
#. Clone this copy to your local disk::

    git clone git@github.com:YourLogin/pyscaffold.git
    cd pyscaffold

#. You should run::

    pip install -U pip setuptools
    pip install -e .

   to be able run ``putup``.

.. TODO: Remove the manual installation/update of pip, setuptools and setuptools_scm
   once pip starts supporting editable installs with pyproject.toml

#. Install ``pre-commit``::

    pip install pre-commit
    pre-commit install

   PyScaffold project comes with a lot of hooks configured to
   automatically help the developer to check the code being written.

#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the master branch!

#. Start your work on this branch. When you’re done editing, do::

    git add modified_files
    git commit

   to record your changes in Git, then push them to GitHub with::

    git push -u origin my-feature

#. Please check that your changes don't break any unit tests with::

    tox

   (after having installed `tox`_ with ``pip install tox`` or ``pipx``).
   Don't forget to also add unit tests in case your contribution
   adds an additional feature and is not just a bugfix.

   To speed up running the tests, you can try to run them in parallel, using
   ``pytest-xdist``. This plugin is already added to the test dependencies, so
   everything you need to do is adding ``-n auto`` or
   ``-n <NUMBER OF PROCESS>`` in the CLI. For example::

    tox -- -n 15

   Please have in mind that PyScaffold test suite is IO intensive, so using a
   number of processes slightly bigger than the available number of CPUs is a
   good idea. For quicker feedback you can also try::

    tox -e fast

#. Use `flake8`_/`black`_ to check\fix your code style.
#. Add yourself to the list of contributors in ``AUTHORS.rst``.
#. Go to the web page of your PyScaffold fork, and click
   "Create pull request" to send your changes to the maintainers for review.
   Find more detailed information `creating a PR`_. You might also want to open
   the PR as a draft first and mark it as ready for review after the feedbacks
   from the continuous integration (CI) system or any required fixes.
#. If you are submitting a change related to an existing CI
   system template (e.g. travis, cirrus, or even tox and pre-commit),
   please consider first submitting a companion PR to PyScaffold's
   `ci-tester`_, with the equivalent files changes, so we are sure it works.

   If you are proposing a new CI system template, please send us a link of a
   simple repository generated with your templates (a simple ``putup --<YOUR
   EXTENSION> ci-tester`` will do) and the CI logs for that repository.

   This helps us a lot to control breaking changes that might appear in the future.

Release
========

New PyScaffold releases should be automatically uploaded to PyPI by one of our
`GitHub actions`_ every time a new tag is pushed to the repository.
Therefore, as a PyScaffold maintainer, the following steps are all you need
to release a new version:

#. Make sure all unit tests on `Cirrus-CI`_ are green.
#. Tag the current commit on the master branch with a release tag, e.g. ``v1.2.3``.
#. Push the new tag to the upstream repository, e.g. ``git push upstream v1.2.3``
#. After a few minutes check if the new version was uploaded to PyPI_

If, for some reason, you need to manually create a new distribution file and
upload to PyPI, the following extra steps can be used:

#. Clean up the ``dist`` and ``build`` folders with ``tox -e clean``
   (or ``rm -rf dist build``)
   to avoid confusion with old builds and Sphinx docs.
#. Run ``tox -e build`` and check that the files in ``dist`` have
   the correct version (no ``.dirty`` or Git hash) according to the Git tag.
   Also sizes of the distributions should be less than 500KB, otherwise unwanted
   clutter may have been included.
#. Run ``tox -e publish -- --repository pypi`` and check that everything was
   uploaded to `PyPI`_ correctly.

After successful releases (specially of new major versions), it is a good
practice to re-generate our example repository. To manually do that, please
visit our `GitHub actions`_ page and run the **Make Demo Repo** workflow
(please check if it was not automatically triggered already).


Troubleshooting
===============

    I've got a strange error related to versions in ``test_update.py`` when
    executing the test suite or about an *entry_point* that cannot be found.

Make sure to fetch all the tags from the upstream repository, the command ``git
describe --abbrev=0 --tags`` should return the version you are expecting. If
you are trying to run the CI scripts in a fork repository, make sure to push
all the tags.
You can also try to remove all the egg files or the complete egg folder, i.e.
``.eggs``, as well as the ``*.egg-info`` folders in the ``src`` folder or
potentially in the root of your project. Afterwards run ``python setup.py
egg_info --egg-base .`` again.

    I've got a strange syntax error when running the test suite. It looks
    like the tests are trying to run with Python 2.7 …

Try to create a dedicated venv using Python 3.6+ (or the most recent version
supported by PyScaffold) and use a ``tox`` binary freshly installed in this
venv. For example::

    python3 -m venv .venv
    source .venv/bin/activate
    .venv/bin/pip install tox
    .venv/bin/tox -e all

..

    I am trying to debug the automatic test suite, but it is very hard to
    understand what is happening.

`Pytest can drop you`_ in a interactive session in the case an error occurs.
In order to do that you need to pass a ``--pdb`` option (for example by running
``tox -- -k NAME_OF_THE_FALLING_TEST --pdb``).
While ``pdb`` does not have the best user interface in the world, if you feel
courageous, it is possible to use an alternate implementation like `ptpdb`_ and
`bpdb`_ (please notice some of them might require additional options, such as
``--pdbcls ptpdb:PtPdb``/``--pdbcls bpdb:BPdb``). You will need to temporarily
add the respective package as a dependency in your ``tox.ini`` file.
You can also setup breakpoints manually instead of using the ``--pdb`` option.


.. _Travis: https://travis-ci.org/pyscaffold/pyscaffold
.. _Cirrus-CI: https://cirrus-ci.com/github/pyscaffold/pyscaffold
.. _PyPI: https://pypi.python.org/
.. _Blue Yonder: http://www.blue-yonder.com/en/
.. _project repository: https://github.com/pyscaffold/pyscaffold/
.. _Git: http://git-scm.com/
.. _Miniconda: https://conda.io/miniconda.html
.. _issue tracker: http://github.com/pyscaffold/pyscaffold/issues
.. _Create a Gitub account: https://github.com/signup/free
.. _creating a PR: https://help.github.com/articles/creating-a-pull-request/
.. _tox: https://tox.readthedocs.io/
.. _flake8: http://flake8.pycqa.org/
.. _ci-tester: https://github.com/pyscaffold/ci-tester
.. _Pytest can drop you: https://docs.pytest.org/en/stable/usage.html#dropping-to-pdb-python-debugger-at-the-start-of-a-test
.. _ptpdb: https://pypi.org/project/ptpdb/
.. _bpdb: https://docs.bpython-interpreter.org/en/latest/bpdb.html?highlight=bpdb
.. _black: https://pypi.org/project/black/
.. _GitHub actions: https://github.com/pyscaffold/pyscaffold/actions
