.. image:: gfx/logo.png
   :height: 512px
   :width: 512px
   :scale: 60 %
   :alt: PyScaffold logo
   :align: center

|

PyScaffold helps you to easily setup a new Python project, it is as easy as::

    putup my_project

This will create a new folder ``my_project`` containing a perfect *project
template* with everything you need for some serious coding. After the usual::

   python setup.py develop

you are all set and ready to go, meaning that in a Python shell you can do:

.. code-block:: python

   >>> from my_project.skeleton import fib
   >>> fib(10)
   55

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have `Git  <http://git-scm.com/>`_ installed and set up on your PC,
meaning at least your name and email configured.
The project template in ``my_project`` provides you with a lot of
:ref:`features <features>`. PyScaffold is compatible with Python 2.7 and Python
greater equal 3.4.


.. note::

   Currently PyScaffold 3.0 needs at least Python 3.4 due to a `bug in setuptools`_
   that only affects Python 2. For the time being use PyScaffold 2.5.8 for Python 2.7
   instead.

Contents
--------

.. toctree::
   :maxdepth: 2

   Features <features>
   Installation <install>
   Examples <examples>
   Configuration <configuration>
   Extending PyScaffold <extensions>
   Embedding PyScaffold <python-api>
   Cookiecutter Integration <cookiecutter-integration>
   Contributions & Help <contributing>
   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _bug in setuptools: https://github.com/pypa/setuptools/issues/1136
