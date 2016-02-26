.. _examples:

========
Examples
========

Just a few examples to get you an idea of how easy PyScaffold is to use:

``putup my_little_project``
  The simplest way of using PyScaffold. A directory ``my_little_project`` is
  created with a Python package named exactly the same. Only a simple copyright
  statement is used as license.

``putup skynet -l gpl3 -d "Finally, the ultimate AI!" -u http://sky.net``
  This will create a project and package named *skynet* licensed under the GPL3.
  The *summary* inside ``setup.cfg`` is directly set to "Finally, the ultimate AI!"
  and the homepage to http://sky.net.

``putup Scikit-Gravity -p skgravity -l new-bsd``
  This will create a project named *Scikit-Gravity* but the package will be
  named *skgravity* with license new-BSD.

``putup youtub --with-django --with-pre-commit  -d "Ultimate video site for hot tub fans"``
  This will create a web project and package named *youtub* that also includes
  the files created by `Django's <https://www.djangoproject.com/>`_
  ``django-admin``. The summary description in ``setup.cfg`` will be set and
  a file ``.pre-commit-config.yaml`` is created with a default setup for
  `pre-commit <http://pre-commit.com/>`_.

``putup thoroughly_tested --with-tox --with-travis``
  This will create a project and package *thoroughly_tested* with files ``tox.ini``
  and ``.travis.yml`` for `Tox <http://tox.testrun.org/>`_ and
  `Travis <https://travis-ci.org/>`_.

``putup my_zope_subpackage --with-namespace zope -l gpl3``
  This will create a project and subpackage named *my_zope_subpackage* in the
  namespace *zope*. To be honest, there is really only the `Zope project <http://www.zope.org/>`_
  that comes to my mind which is using this exotic feature of Python's packaging system.
  Chances are high, that you will never ever need a namespace package in your life.
