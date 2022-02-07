============
Contributing
============

PyScaffold was started by `Blue Yonder`_ developers to help automating and
standardizing the process of project setups. Nowadays it is a pure community
project driven by volunteer work.
Every little gesture is really appreciated (including issue reports!),
and if you are interested in joining our continuous effort for making PyScaffold
better, welcome aboard! We are pleased to help you in this journey |:ship:|.

.. note::
   This document is an attempt to get any potential contributor familiarized
   with PyScaffold's community processes, but by no means is intended to be a
   complete reference.

   Please feel free to contact us for help and guidance in our `GitHub discussions`_ page.

Please notice, all the members of the PyScaffold community (and in special
contributors) are expected to be **open, considerate, reasonable, and respectful**.
and follow the `Python Software Foundation's Code of Conduct`_ when interacting
with PyScaffold's codebases, issue trackers, chat rooms and mailing lists (or
equivalent).

.. tip::
   If you are new to open source or have never contributed before to a software
   project, please have a look at `contribution-guide.org`_ and the
   `How to Contribute to Open Source`_ guide.
   Other resources are also listed in the excellent `guide created by FreeCodeCamp`_.


How to contribute to PyScaffold?
================================

This guide focus on issue reports, documentation improvements, and code
contributions, but there are many other ways to contribute to PyScaffold,
even if you are not an experienced programmer or don't have the time to code.
Skills like graphical design, event planning, teaching, mentoring, public outreach,
tech evangelism, code review, between `many others`_ are greatly appreciated.
Please `reach us out`_, we would love to have you on board and discuss what can
be done!


|:bug:| Issue Reports
---------------------

If you experience bugs or general issues with PyScaffold, please have a look
on our `issue tracker`_.

.. note::
   Please don't forget to include the closed issues in your search_.
   Sometimes another person has already experienced your problem and reported a
   solution. If you don't see anything useful there, feel free to fire a
   new issue report |:wink:|

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.


|:books:| Documentation Improvements
------------------------------------

You can help us improve our docs by making them more readable and coherent, or
by adding missing information and correcting mistakes (including spelling and
grammar errors).

Already known and discussed documentation issues that would benefit from
contributions are marked in our `issue tracker`_ with the **documentation**
label (we also do the same for all existing extensions under the `PyScaffold
organization`_ on GitHub). But you are also welcomed to propose completely new
changes (e.g., if you find new problems or would like to see a complicated topic
better explained).

PyScaffold's documentation is written in `reStructuredText`_ and uses `Sphinx`_
as its main documentation compiler [#contrib1]_. This means that the docs are
kept in the same repository as the project code, and that any documentation
update is done via GitHub pull requests, as if it was a code contribution.

While that might be scary for new programmers, it is actually a very nice way
of getting started in the open source community, since doc contributions are
not as difficult to make as other code contributions (for example, they don't
require any automated testing).

Please have a look in the steps described below and in case of doubts, contact
us at the `GitHub discussions`_ page for help.

When working on changes to PyScaffold's docs in your local machine, you can
compile them using |tox|_::

    tox -e docs

and use Python's built-in web server for a preview in your web browser
(``http://localhost:8000``)::

    python3 -m http.server --directory 'docs/_build/html'

.. tip::
   Please notice that the `GitHub web interface`_ provides a quick way of
   propose changes in PyScaffold's files, that do not require you to have a lot
   of experience with git_ or programing in general. While this mechanism can
   be tricky for normal code contributions, it works perfectly fine for
   contributing to the docs, and can be quite handy.

   If you are interested in trying this method out, please navigate to
   PyScaffold's ``docs`` folder in the `main repository`_, find which file you
   would like to propose changes and click in the little pencil icon at the
   top, to open `GitHub's code editor`_. Once you finish editing the file,
   please write a nice message in the form at the bottom of the page describing
   which changes have you made and what are the motivations behind them and
   submit your proposal.


|:computer:| Code Contributions
-------------------------------

PyScaffold uses `GitHub's fork and pull request workflow`_ for code
contributions, which means that anyone can propose changes in the code base.

Once proposed changes are submitted, our continuous integration (CI) service,
`Cirrus-CI`_, will run a series of automated checks to make sure everything is
OK and the pull request (PR) itself will be reviewed by one of PyScaffold
maintainers, before being merged in the code base. In some cases, changes might
be required to fix problems pointed out by the CI, or the maintainers might
want to discuss a bit about the PR and suggest adjustments. Please don't worry
if that happens, this kind of iterative development is very common in the open
source community and usually makes the software better. Besides, we will do our
best to provide feedback (and support for eventual doubts) as soon as we can.

If you are unsure about what to contribute, please have a look in our `issue
tracker`_ (or the issue tracker of any extension under the `PyScaffold
organization`_ on GitHub). Contributions on issues marked with the **help
wanted** label are particularly appreciated. Moreover, the **good first issue**
label marks issues that do not require a huge understanding on how the project
works and therefore can be tackled by new members of the community. Please also
notice that some issues are not ready yet for a follow up implementation or bug
fix, these are usually signed with other labels_, such as **needs discussion**
and **waiting response**. When in doubt, please engage in the conversation by
posting a message to the open issue.

Understanding how PyScaffold works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a change in mind, but don't know how to implement it, please have a
look in our :doc:`/dev-guide`. It explains the main aspects of PyScaffold
internals and provide a brief overview of how the project is organized.

Submit an issue
~~~~~~~~~~~~~~~

Before you work on any non-trivial code contribution it's best to first create
an `issue report`_ to start a discussion on the subject.
This often provides additional considerations and avoids unnecessary work.

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Before you start coding, we recommend creating an isolated `virtual
environment`_ to avoid any problems with your installed Python packages.
This can easily be done via either |virtualenv|_::

    virtualenv <PATH TO VENV>
    source <PATH TO VENV>/bin/activate

or Miniconda_::

    conda env create -d environment.yml
    conda activate pyscaffold

Clone the repository
~~~~~~~~~~~~~~~~~~~~

#. `Create a GitHub account`_  if you do not already have one.
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

Implement your changes
~~~~~~~~~~~~~~~~~~~~~~

#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the master branch!

#. Start your work on this branch. Don't forget to add docstrings_ to new
   functions, modules and classes, especially if they are part of public APIs.

#. Add yourself to the list of contributors in ``AUTHORS.rst``.

#. When you’re done editing, do::

    git add <MODIFIED FILES>
    git commit

   to record your changes in git_. Please make sure to see the validation
   messages from |pre-commit|_ and fix any eventual issues.
   This should automatically use flake8_/black_ to check/fix the code style
   in a way that is compatible with PyScaffold.

   .. important:: Don't forget to add unit tests and documentation in case your
      contribution adds an additional feature and is not just a bugfix.

      Moreover, writing a `descriptive commit message`_ is highly recommended.
      In case of doubt, you can check the commit history with::

         git log --graph --decorate --pretty=oneline --abbrev-commit --all

      to look for recurring communication patterns.

#. Please check that your changes don't break any unit tests with::

    tox

   (after having installed |tox|_ with ``pip install tox`` or ``pipx``).

   To speed up running the tests, you can try to run them in parallel, using
   ``pytest-xdist``. This plugin is already added to the test dependencies, so
   everything you need to do is adding ``-n auto`` or
   ``-n <NUMBER OF PROCESSES>`` in the CLI. For example::

    tox -- -n 15

   Please have in mind that PyScaffold test suite is IO intensive, so using a
   number of processes slightly bigger than the available number of CPUs is a
   good idea. For quicker feedback you can also try::

    tox -e fast

   or select individual tests using the ``-k`` flag from pytest_::

    tox -- -k <NAME OF THE TEST FUNCTION>

   You can also use |tox|_ to run several other pre-configured tasks in the
   repository. Try ``tox -av`` to see a list of the available checks.

Submit your contribution
~~~~~~~~~~~~~~~~~~~~~~~~

#. If everything works fine, push your local branch to GitHub with::

    git push -u origin my-feature

#. Go to the web page of your PyScaffold fork and click
   "Create pull request" to send your changes to the maintainers for review.
   Find more detailed information in `creating a PR`_. You might also want to open
   the PR as a draft first and mark it as ready for review after the feedbacks
   from the continuous integration (CI) system or any required fixes.

#. If you are submitting a change related to an existing CI
   system template (e.g., travis, cirrus, or even tox and pre-commit),
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
You can also try to remove all the egg files or the complete egg folder, i.e.,
``.eggs``, as well as the ``*.egg-info`` folders in the ``src`` folder or
potentially in the root of your project.

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

Sometimes |tox|_ misses out when new dependencies are added, especially to
``setup.cfg`` and ``docs/requirements.txt``. If you find any problems with
missing dependencies when running a command with |tox|_, try to recreate the
``tox`` environment using the ``-r`` flag. For example, instead of::

    tox -e docs

Try running::

    tox -r -e docs

..

    I am trying to debug the automatic test suite, but it is very hard to
    understand what is happening.

`Pytest can drop you`_ in an interactive session in the case an error occurs.
In order to do that you need to pass a ``--pdb`` option (for example by running
``tox -- -k <NAME OF THE FALLING TEST> --pdb``).
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
pull requests`_, or going through the open issues and evaluating them according to our
labels_ and even suggesting possible solutions or workarounds.


|:hammer_and_wrench:| Maintainer tasks
--------------------------------------

PyScaffold maintainers not only carry out most of the source code development,
but also are responsible for planning new releases, reviewing pull requests,
and managing CI tools between many other tasks. If you are interested in
becoming a maintainer, the best is to keep "hanging out" in the community,
helping with the issues, proposing PRs and doing some code review (either in
the `main repository`_ or the extensions under the `PyScaffold organization`_
on GitHub).  Eventually, one of the existing maintainers will approach you and
ask you to join |:wink:|.

This section describes some technical aspects of recurring tasks
and is meant as a guide for new maintainers (or old ones that need a memory
refresher).


Releases
~~~~~~~~

New PyScaffold releases should be automatically uploaded to PyPI by one of our
`GitHub actions`_ every time a new tag is pushed to the repository.
Therefore, as a PyScaffold maintainer, the following steps are all you need
to release a new version:

#. Make sure all unit tests on `Cirrus-CI`_ are green.
#. Tag the current commit on the master branch with a release tag, e.g., ``v1.2.3``.
#. Push the new tag to the upstream repository, e.g., ``git push upstream v1.2.3``
#. After a few minutes check if the new version was uploaded to PyPI_

If, for some reason, you need to manually create a new distribution file and
upload to PyPI, the following extra steps can be used:

#. Clean up the ``dist`` and ``build`` folders with ``tox -e clean``
   (or ``rm -rf dist build``)
   to avoid confusion with old builds and Sphinx docs.
#. Run ``tox -e build`` and check that the files in ``dist`` have
   the correct version (no ``.dirty`` or git_ hash) according to the git_ tag.
   Also sizes of the distributions should be less than 500KB, otherwise unwanted
   clutter may have been included.
#. Run ``tox -e publish -- --repository pypi`` and check that everything was
   uploaded to `PyPI`_ correctly.

.. important::
   When working in a new **external extension**, it is important that the first
   distribution is manually uploaded to PyPI_, to make sure it will have the
   correct ownership.

After successful releases (especially of new major versions), it is a good
practice to re-generate our example repository. To manually do that, please
visit our `GitHub actions`_ page and run the **Make Demo Repo** workflow
(please check if it was not automatically triggered already).


Working on multiple branches and splitting complex changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyScaffold follows `semantic versioning`_. As a consequence, most of the times
the ``master`` (or ``main``) branch for either the `main repository`_ or the
extensions under the `PyScaffold organization`_ on GitHub, should be pointing
out to the latest published minor version, or the next minor version still
under development. We also tend (but are not committed to) keep some level of
support for the previous major version, which means that once a major version
is superseded, the maintainers should create a new branch pointing to this
previous version.

For this reason, `Read the Docs`_ should always be configured to show the
**stable** version by default instead of **latest**. The **stable** version
corresponds to the latest commit that received a git_ tag, while the **latest**
version points to the **master**/**main** branch.

During the transition period between major versions, it is common practice to
create a new *development* version that is kept apart from the master branch
and will only be merged when everything is ready for release. For example, a
``v4.0.x`` branch was used for all the development related to PyScaffold v4,
while the ``master`` branch was still being used for bug fixes to v3.

When working in complex features or refactoring, it might also be interesting
to create a new long-living branch that will receive multiple PRs from other
short-lived auxiliary branch splitting the changes into smaller steps. Please
be aware that splitting complex changes into smaller PRs can be very tricky.
Whenever possible, try to create independent PRs, i.e., PRs that can be merged
independently into a long-living branch, without causing conflicts between
themselves. When that is not possible, please coordinate a review and merge
strategy with the other maintainers reviewing your code.

One possible strategy is to create a single PR, but ask your reviewers to
consider each commit (that should be small) as if it was an independent PR.
A different strategy is to use **stacked PRs**, as described by the following
references:

- `Timothy Andrew's Blog <https://0xc0d1.com/blog/git-stack/>`_
- `Doctor McKayla's Blog <https://www.michaelagreiler.com/stacked-pull-requests/>`_
- `Div's Blog <https://divyanshu013.dev/blog/code-review-stacked-prs>`_
- `LogRocket's Blog <https://blog.logrocket.com/using-stacked-pull-requests-in-github>`_

Please also notice that independently of the strategy you and the reviewers
agree on, it might be worthy to ask them to just review the PRs without merging
(so you are responsible for closing the PRs and bringing their code to the
long-lived branch via git ``merge``, ``pull`` or ``cherry-pick``).
This might avoid confusion since GitHub does not provide any special mechanism
for dealing with dependencies between PRs. Moreover, the merging might be just
easier via git_ CLI.

.. note::
   PyScaffold's repositories also contain ``archives/*`` branches. These
   branches correspond to old experiments and alternative feature
   implementations that, although not merged, are kept for reference as
   interesting (or very complex) pieces of code that might be useful in the
   future.


|:mega:| Spread the Word
------------------------

Finally, another way to contribute to PyScaffold is to recommend it. You can
speak about it with your work colleagues, in a conference, or even writing a
blog post about the project.

If you need to pitch PyScaffold to your boss or co-workers, please check out
our docs. We have enumerated a few :doc:`reasons for using PyScaffold
</reasons>` in our website, that can be handy to have around |:wink:|.



.. [#contrib1] The same is valid for the extensions under the `PyScaffold
   organization`_ on GitHub, although some extension, like
   `pyscaffoldext-markdown`_ and `pyscaffoldext-dsproject`_ use CommonMark_
   with MyST_ extensions as an alternative to reStructuredText_.



.. |virtualenv| replace:: ``virtualenv``
.. |pre-commit| replace:: ``pre-commit``
.. |tox| replace:: ``tox``

.. _black: https://pypi.org/project/black/
.. _Blue Yonder: https://blueyonder.com/
.. _bpdb: https://docs.bpython-interpreter.org/en/latest/bpdb.html?highlight=bpdb
.. _ci-tester: https://github.com/pyscaffold/ci-tester
.. _Cirrus-CI: https://cirrus-ci.com/github/pyscaffold/pyscaffold
.. _CommonMark: https://commonmark.org/
.. _contribution-guide.org: https://www.contribution-guide.org/
.. _Create a GitHub account: https://github.com/join
.. _creating a PR: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
.. _descriptive commit message: https://chris.beams.io/posts/git-commit
.. _docstrings: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _flake8: https://flake8.pycqa.org/en/stable/
.. _git: https://git-scm.com/
.. _GitHub actions: https://github.com/pyscaffold/pyscaffold/actions
.. _GitHub's fork and pull request workflow: https://guides.github.com/activities/forking/
.. _guide created by FreeCodeCamp: https://github.com/FreeCodeCamp/how-to-contribute-to-open-source
.. _issue tracker: https://github.com/pyscaffold/pyscaffold/issues
.. _issue report: https://github.com/pyscaffold/pyscaffold/issues
.. _labels: https://github.com/pyscaffold/pyscaffold/labels
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _MyST: https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html
.. _pre-commit: https://pre-commit.com/
.. _ptpdb: https://pypi.org/project/ptpdb/
.. _PyPI: https://pypi.org
.. _PyScaffold organization: https://github.com/pyscaffold
.. _pyscaffoldext-dsproject: https://github.com/pyscaffold/pyscaffoldext-dsproject
.. _pyscaffoldext-markdown: https://github.com/pyscaffold/pyscaffoldext-markdown
.. _Pytest can drop you: https://docs.pytest.org/en/stable/how-to/failures.html#using-python-library-pdb-with-pytest
.. _pytest: https://docs.pytest.org/en/stable/
.. _Python Software Foundation's Code of Conduct: https://www.python.org/psf/conduct/
.. _Read the Docs: https://docs.readthedocs.io/en/stable/versions.html
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
.. _reviewing existing open pull requests: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
.. _search: https://github.com/pyscaffold/pyscaffold/issues?q=
.. _semantic versioning: https://semver.org
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/en/stable/
.. _Travis: https://travis-ci.org/pyscaffold/pyscaffold
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/

.. _project repository: https://github.com/pyscaffold/pyscaffold
.. _main repository: https://github.com/pyscaffold/pyscaffold

.. _GitHub discussions: https://github.com/pyscaffold/pyscaffold/discussions
.. _reach us out: https://github.com/pyscaffold/pyscaffold/discussions

.. _GitHub web interface: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files
.. _GitHub's code editor: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files

.. _How to Contribute to Open Source: https://opensource.guide/how-to-contribute
.. _ways of contributing: https://opensource.guide/how-to-contribute/
.. _many others: https://opensource.guide/how-to-contribute/
