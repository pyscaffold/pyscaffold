============
Contributing
============

PyScaffold was started by `Blue Yonder`_ developers to help automating and
standardizing the process of project setups. Nowadays it is a pure community
project driven by volunteer work.
Every little gesture is really appreciated (including |:bug:| issue reports!),
and if you are interested in joining our continuous effort for making PyScaffold
better, welcome aboard! We are pleased to help you in this journey |:ship:|.

.. note::
   This document is an attempt to get any potential contributor familiarised
   with PyScaffold's community processes, but by no means is intended to be a
   complete reference.

   Please feel free to contact us for help and guidance in our `GitHub discussions`_ page.

Please notice, all the members of the PyScaffold community (and in special
contributors) are expected to be **open, considerate, reasonable and respectful**.
When in doubt, `Python Software Foundation's Code of Conduct`_ is a good
reference in terms of community guidelines.

.. tip::
   If you are new to open source or have never contributed before to a software
   community, please have a look at `contribution-guide.org`_ and the
   `How to Contribute to Open Source`_ guide.
   Other resources are also listed in the excelent `guide created by FreeCodeCamp`_.


How to contribute to PyScaffold?
================================

This guide focus on issue reports, documentation improvements, and code
contributions, but there are many other ways to contribute to PyScaffold,
even if you are not an experienced programmer or don't have the time to code.
Skills like graphical design, event planing, teaching, mentoring, public outreach,
tech evangelism, code review, between `many others`_ are greatly appreciated.
Please `reach us out`_, we would love to have you on board and discuss what can
be done!


|:beetle:| Issue Reports
------------------------

If you experience bugs or in general issues with PyScaffold, please have a look
on our `issue tracker`_ (sometimes another person have already experienced your
problem and reported a solution). If you don't see anything useful there, please feel
free to fire an issue report.


|:books:| Documentation Improvements
------------------------------------

Did you find any problems with our documentation and have some time to spare?
Any spelling error? Or is there any complicated topic that you didn't find
particularly well explained?
You can help us improve our docs by making them more readable and coherent, or
by adding missing information and correcting mistakes.

PyScaffold's documentation is written in `reStructuredText`_ and uses `Sphinx`_
as its main documentation compiler. This means that the docs are kept in the
same repository as the project code, and that any documentation update is done
via GitHub pull requests, as if it was a code contribution.

While that might be scary for new programmers, it is actually a very nice way
of getting started in the open source community, since doc contributions are
not as difficult to make as other code contributions (for example, they don't
require any automated testing).

Please have a look in the steps described bellow and in case of doubts, contact
us at the `GitHub discussions`_ page for help.

.. tip::
   Please notice that the `GitHub web interface`_ provides a quick way of
   propose changes in PyScaffold's files, that do not require you to have a lot
   of experience with git_ or programing in general.  While this mechanism can
   be tricky for normal code contributions, it works perfectly fine for
   contributing to the docs, and can be quite handy.

   If you are interested in trying this method out, please navigate to
   PyScaffold's `docs` folder in the `main repository`_, find which file you
   would like to propose changes and click in the little pencil icon at the
   top, to open `GitHub's code editor`_. Once you finish editing the file,
   please write a nice message in the form at the bottom of the page describing
   which changes have you made and what are the motivations behind them, and
   submit your proposal.


|:computer:| Code Contributions
-------------------------------

Understanding how PyScaffold works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main aspects of PyScaffold internals are explained in our
:doc:`/dev-guide`. Please make sure to check it out for a brief overview of the
project and how it is organized.

Submit an issue
~~~~~~~~~~~~~~~

Before you work on any non-trivial code contribution it's best to first create
an issue report to start a discussion on the subject. This often provides
additional considerations and avoids unnecessary work.

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Before you start coding we recommend to create an isolated `virtual
environment`_ to avoid any problems with your installed Python packages.
This can easily be done via either |virtualenv|_::

    virtualenv <PATH TO VENV>
    source <PATH TO VENV>/bin/activate

or Miniconda_::

    conda create -n pyscaffold python=3 six virtualenv pytest pytest-cov
    conda activate pyscaffold

Clone the repository
~~~~~~~~~~~~~~~~~~~~

#. `Create a Gitub account`_  if you do not already have one.
#. Fork the `project repository`_: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on the GitHub server.
#. Clone this copy to your local disk::

    git clone git@github.com:YourLogin/pyscaffold.git
    cd pyscaffold

#. You should run::

    pip install -U pip setuptools -e .

   to be able run ``putup --help``.

#. Install |pre-commit|_::

    pip install pre-commit
    pre-commit install

   PyScaffold project comes with a lot of hooks configured to
   automatically help the developer to check the code being written.

#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the master branch!

#. Start your work on this branch.

#. Add yourself to the list of contributors in ``AUTHORS.rst``.

#. When you’re done editing, do::

    git add <MODIFIED FILES>
    git commit

   to record your changes in Git. Please make sure to see the validation
   messages from |pre-commit|_ and fix any eventual issue.
   This should automatically use flake8_/black_ to check/fix the code style
   in a way that is compatible with PyScaffold.

#. Please check that your changes don't break any unit tests with::

    tox

   (after having installed |tox|_ with ``pip install tox`` or ``pipx``).
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

   or select individual tests using the ``-k`` flag from pytest_::

    tox -- -k <NAME OF THE TEST FUNCTION>

   You can also use |tox|_ to run several other pre-configured tasks in the
   repository. Try ``tox -av`` to see a list of the available checks.

#. If everything works fine, push your local branch to GitHub with::

    git push -u origin my-feature

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


Troubleshooting
~~~~~~~~~~~~~~~

    I've got a strange error related to versions in ``test_update.py`` when
    executing the test suite or about an ``entry_point`` that cannot be found.

Make sure to fetch all the tags from the upstream repository, the command ``git
describe --abbrev=0 --tags`` should return the version you are expecting. If
you are trying to run the CI scripts in a fork repository, make sure to push
all the tags.
You can also try to remove all the egg files or the complete egg folder, i.e.
``.eggs``, as well as the ``*.egg-info`` folders in the ``src`` folder or
potentially in the root of your project. Afterwards run ``python setup.py
egg_info --egg-base .`` again.

..

    I've got a strange syntax error when running the test suite. It looks
    like the tests are trying to run with Python 2.7 …

Try to create a dedicated `virtual environment`_ using Python 3.6+ (or the most
recent version supported by PyScaffold) and use a |tox|_ binary freshly
installed. For example::

    virtualenv .venv
    source .venv/bin/activate
    .venv/bin/pip install tox
    .venv/bin/tox -e all

..

    I have found a weird error when running |tox|_. It seems like some dependency
    is not being installed.

Sometimes |tox|_ misses out when new dependencies are added, specially to
``setup.cfg`` and ``docs/requirements.txt``. If you find any problems with
missing dependencies when running a command with |tox|_, try to recreate the
``tox`` environment using the ``-r`` flag. For example, instead of::

    tox -e docs

Try running::

    tox -r -e docs

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


|:mag:| Code Reviews and Issue Triage
-------------------------------------

If you are an experienced developer and wants to help, but do not have the time
to create complete pull requests, you can still help by `reviewing existing open
pull requests`_, or going through the open issues and evaluating them according to `our
labels`_ and even suggesting possible solutions or workarounds.


|:hammer_and_wrench:| Maintainer tasks
--------------------------------------

Releases
~~~~~~~~

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

.. tip::
   When working in a new **external extension**, it is important that the first
   distribution is manually uploaded to PyPI_, to make sure it will have the
   correct ownership.

After successful releases (specially of new major versions), it is a good
practice to re-generate our example repository. To manually do that, please
visit our `GitHub actions`_ page and run the **Make Demo Repo** workflow
(please check if it was not automatically triggered already).


|:mega:| Spread the Word
------------------------

Finally, another way to contribute to PyScaffold is to recommend it. You can
speak about it with your work colleagues, in a conference, or even writing a
blog post about the project.

If you need to pitch PyScaffold to you boss or co-workers, please checkout our
docs. We have enumerated a few :doc:`reasons for using PyScaffold </reasons>`
in our website, that can be handy to have around |:wink:|.



.. |virtualenv| replace:: ``virtualenv``
.. |pre-commit| replace:: ``pre-commit``
.. |tox| replace:: ``tox``

.. _Blue Yonder: https://blueyonder.com/
.. _Cirrus-CI: https://cirrus-ci.com/github/pyscaffold/pyscaffold
.. _Create a Gitub account: https://github.com/join
.. _Git: https://git-scm.com/
.. _GitHub actions: https://github.com/pyscaffold/pyscaffold/actions

.. _GitHub discussions: https://github.com/pyscaffold/pyscaffold/discussions
.. _reach us out: https://github.com/pyscaffold/pyscaffold/discussions

.. _GitHub web interface: https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository
.. _GitHub's code editor: https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository

.. _How to Contribute to Open Source: https://opensource.guide/how-to-contribute
.. _ways of contributing: https://opensource.guide/how-to-contribute/
.. _many others: https://opensource.guide/how-to-contribute/

.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _PyPI: https://pypi.org/
.. _Pytest can drop you: https://docs.pytest.org/en/stable/usage.html#dropping-to-pdb-python-debugger-at-the-start-of-a-test
.. _Python Software Foundation's Code of Conduct: https://www.python.org/psf/conduct/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Travis: https://travis-ci.org/pyscaffold/pyscaffold
.. _black: https://pypi.org/project/black/
.. _bpdb: https://docs.bpython-interpreter.org/en/latest/bpdb.html?highlight=bpdb
.. _ci-tester: https://github.com/pyscaffold/ci-tester
.. _contribution-guide.org: http://www.contribution-guide.org/
.. _creating a PR: https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
.. _flake8: https://flake8.pycqa.org/en/stable/
.. _guide created by FreeCodeCamp: https://github.com/FreeCodeCamp/how-to-contribute-to-open-source
.. _issue tracker: https://github.com/pyscaffold/pyscaffold/issues
.. _our labels: https://github.com/pyscaffold/pyscaffold/labels
.. _pre-commit: https://pre-commit.com/

.. _project repository: https://github.com/pyscaffold/pyscaffold
.. _main repository: https://github.com/pyscaffold/pyscaffold

.. _ptpdb: https://pypi.org/project/ptpdb/
.. _pytest: https://docs.pytest.org/en/stable/
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
.. _reviewing existing open pull requests: https://docs.github.com/en/github/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
.. _tox: https://tox.readthedocs.io/en/stable/
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
