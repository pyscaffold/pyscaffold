============
Contributing
============

PyScaffold is developed by `Blue Yonder`_ developers to help automating and
standardizing the process of project setups.
You are very welcome to join in our effort if you would like to contribute.

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
to setup a dedicated development environment for Python with::

   conda create -n pyscaffold 'python==3' virtualenv

Then activate the environment `pyscaffold` with::

   source activate pyscaffold

Clone the repository
--------------------

#. `Create a Gitub account`_  if you do not already have one.
#. Fork the project repository: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on the GitHub server.
#. Clone this copy to your local disk::

    git clone git@github.com:YourLogin/pyscaffold.git

#. Run ``python setup.py egg_info`` after a fresh checkout. This will generate
   some critically needed files.
#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the master branch!

#. Start your work on this branch. When you’re done editing, do::

    git add modified_files
    git commit

   to record your changes in Git, then push them to GitHub with::

    git push -u origin my-feature

#. Go to the web page of your PyScaffold fork, and click
   "Create pull request" to send your changes to the maintainers for review.
   Find more detailed information `creating a PR`_.

If you would like to contribute to PyScaffold, fork the `main repository`_
on GitHub with the help of Git_, then submit a “pull request” (PR):

.. _Blue Yonder: http://www.blue-yonder.com/en/
.. _main repository: https://github.com/blue-yonder/pyscaffold/
.. _Git: http://git-scm.com/
.. _chat: https://gitter.im/blue-yonder/pyscaffold
.. _Miniconda: https://conda.io/miniconda.html
.. _issue tracker: http://github.com/blue-yonder/pyscaffold/issues
.. _Create a Gitub account: https://github.com/signup/free
.. _creating a PR: https://help.github.com/articles/creating-a-pull-request/