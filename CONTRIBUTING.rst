============
Contributing
============

PyScaffold was started by `Blue Yonder`_ developers to help automating and
standardizing the process of project setups. Nowadays it is a pure community
project and you are very welcome to join in our effort if you would like
to contribute.

Chat
====

Join our chat_ to get in direct contact with the developers of PyScaffold.


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
#. Use `flake8`_ to check your code style.
#. Add yourself to the list of contributors in ``AUTHORS.rst``.
#. Go to the web page of your PyScaffold fork, and click
   "Create pull request" to send your changes to the maintainers for review.
   Find more detailed information `creating a PR`_.

Release
=======

As a PyScaffold maintainer following steps are needed to release a new version:

#. Make sure all unit tests on `Travis`_ are green.
#. Tag the current commit on the master branch with a release tag, e.g. ``v1.2.3``.
#. Clean up the ``dist`` and ``build`` folders with ``rm -rf dist build``
   to avoid confusion with old builds and Sphinx docs.
#. Run ``python setup.py test_release`` and check that the files in ``dist`` have
   the correct version (no ``.dirty`` or Git hash) according to the Git tag.
   Also sizes of the distributions should be less then 500KB, otherwise unwanted
   clutter may have been included.
#. Run ``python setup.py release`` and that everything was uploaded to `PyPI`_ correctly.

.. _Travis: https://travis-ci.org/blue-yonder/pyscaffold
.. _PyPI: https://pypi.python.org/
.. _Blue Yonder: http://www.blue-yonder.com/en/
.. _project repository: https://github.com/blue-yonder/pyscaffold/
.. _Git: http://git-scm.com/
.. _chat: https://gitter.im/blue-yonder/pyscaffold
.. _Miniconda: https://conda.io/miniconda.html
.. _issue tracker: http://github.com/blue-yonder/pyscaffold/issues
.. _Create a Gitub account: https://github.com/signup/free
.. _creating a PR: https://help.github.com/articles/creating-a-pull-request/
.. _tox: https://tox.readthedocs.io/
.. _flake8: http://flake8.pycqa.org/
