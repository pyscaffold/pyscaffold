.. _examples:

========
Examples
========

Just a few examples to get you an idea of how easy PyScaffold is to use:

``putup my_little_project``
  The simplest way of using PyScaffold. A directory ``my_little_project`` is
  created with a Python package named exactly the same. The MIT license will be used.

``putup -i my_little_project``
  If you are unsure on how to use PyScaffold, or keep typing ``putup --help``
  all the time, the **experimental** ``--interactive`` (or simply ``-i``), is
  your best friend.
  It will open your default text editor with a file containing examples and
  explanations on how to use ``putup`` (think of it as an "editable" ``--help``
  text, once the file is saved and closed all the values you leave there are
  processed by PyScaffold). You might find some familiarities in the way this
  option works with ``git rebase -i``, including the capacity of choosing a
  different text editor by setting the ``EDITOR`` (or ``VISUAL``) environment
  variable in your terminal.

``putup skynet -l GPL-3.0-only -d "Finally, the ultimate AI!" -u http://sky.net``
  This will create a project and package named *skynet* licensed under the GPL3.
  The *description* inside ``setup.cfg`` is directly set to "Finally, the ultimate AI!"
  and the homepage to http://sky.net.

``putup Scikit-Gravity -p skgravity -l BSD-3-Clause``
  This will create a project named *Scikit-Gravity* but the package will be
  named *skgravity* with license new-BSD [#ex1]_.

``putup youtub --django --pre-commit -d "Ultimate video site for hot tub fans"``
  This will create a web project and package named *youtub* that also includes
  the files created by `Django's <https://www.djangoproject.com/>`_
  ``django-admin`` [#ex2]_. The *description* in ``setup.cfg`` will be set and
  a file ``.pre-commit-config.yaml`` is created with a default setup for
  `pre-commit <http://pre-commit.com/>`_.

``putup thoroughly_tested --cirrus``
  This will create a project and package *thoroughly_tested* with files ``tox.ini``
  and ``.cirrus.yml`` for `Tox <http://tox.testrun.org/>`_ and
  `Cirrus CI <https://cirrus-ci.org/>`_.

``putup my_zope_subpackage --name my-zope-subpackage --namespace zope --package subpackage``
  This will create a project under the ``my_zope_subpackage`` directory with
  the *installation name* of ``my-zope-subpackage`` (this is the name used by
  pip_ and PyPI_), but with the following corresponding import statement::

    from zope import subpackage
    # zope is the namespace and subpackage is the package name

  To be honest, there is really only the `Zope project <http://www.zope.org/>`_
  that comes to my mind which is using this exotic feature of Python's packaging system.
  Chances are high, that you will never ever need a namespace package in your life.
  To learn more about namespaces in the Python ecosystem, check `PEP 420`_.


.. [#ex1] Notice the usage of `SPDX identifiers`_ for specifying the license
   in the CLI

.. [#ex2] Requires the installation of pyscaffoldext-django_.


.. _SPDX identifiers: https://spdx.org/licenses/
.. _pyscaffoldext-django: https://pyscaffold.org/projects/django
.. _pip: https://pip.pypa.io
.. _PyPI: https://pypi.org
.. _PEP 420: https://www.python.org/dev/peps/pep-0420/
