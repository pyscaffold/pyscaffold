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

#. Run ``python setup.py egg_info --egg-base .`` after a fresh checkout.
   This will generate some critically needed files. Typically after that,
   you should run ``python setup.py develop`` to be able run ``putup``.

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

    python setup.py test

   or even a more thorough test with ``tox`` after having installed
   `tox`_ with ``pip install tox``.
   Don't forget to also add unit tests in case your contribution
   adds an additional feature and is not just a bugfix.

   To speed up running the tests, you can try to run them in parallel, using
   ``pytest-xdist``. This plugin is already added to the test dependencies, so
   everything you need to do is adding ``-n auto`` or
   ``-n <NUMBER OF PROCESS>`` in the CLI. For example::

    tox -- -n 15

   Please have in mind that PyScaffold test suite is IO intensive, so using a
   number of processes slightly bigger than the available number of CPUs is a
   good idea.

#. Use `flake8`_ to check your code style.
#. Add yourself to the list of contributors in ``AUTHORS.rst``.
#. Go to the web page of your PyScaffold fork, and click
   "Create pull request" to send your changes to the maintainers for review.
   Find more detailed information `creating a PR`_.
#. If you are submitting a change related to an existing continuous integration
   (CI) system template (e.g. travis, cirrus, or even tox and pre-commit),
   please consider first submitting a companion PR to PyScaffold's
   `ci-tester`_, with the equivalent files changes, so we are sure it works.

   If you are proposing a new CI system template, please send us a link of a
   simple repository generated with your templates (a simple ``putup --<YOUR
   EXTENSION> ci-tester`` will do) and the CI logs for that repository.

   This helps us a lot to control breaking changes that might appear in the future.

Release
=======

As a PyScaffold maintainer following steps are needed to release a new version:

#. Make sure all unit tests on `Cirrus-CI`_ are green.
#. Tag the current commit on the master branch with a release tag, e.g. ``v1.2.3``.
#. Clean up the ``dist`` and ``build`` folders with ``rm -rf dist build``
   to avoid confusion with old builds and Sphinx docs.
#. Run ``python setup.py dists`` and check that the files in ``dist`` have
   the correct version (no ``.dirty`` or Git hash) according to the Git tag.
   Also sizes of the distributions should be less than 500KB, otherwise unwanted
   clutter may have been included.
#. Run ``twine upload dist/*`` and check that everything was uploaded to `PyPI`_ correctly.


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
