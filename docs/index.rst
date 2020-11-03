.. image:: gfx/logo.png
   :height: 512px
   :width: 512px
   :scale: 60 %
   :alt: PyScaffold logo
   :align: center

|

PyScaffold helps you setup a new Python project. It is as easy as::

    putup my_project

This will create a new folder called ``my_project`` containing a perfect *project
template* with everything you need for some serious coding. After the usual::

   python setup.py develop

you are all set and ready to go which means in a Python shell you can do the following:

.. code-block:: pycon

   >>> from my_project.skeleton import fib
   >>> fib(10)
   55

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have `Git`_ installed and set up on your PC, meaning at least your name
and email are configured.
The project template in ``my_project`` provides you with a lot of
:ref:`features <features>`. PyScaffold 3 is compatible with Python 3.4 and greater.
For legacy Python 2.7 support please install PyScaffold 2.5. There is also a `video tutorial`_
on how to develop a command-line application with the help of PyScaffold.



Contents
--------

.. toctree::
   :maxdepth: 2

   Features <features>
   Installation <install>
   Examples <examples>
   Configuration <configuration>
   Dependency Management <dependencies>
   Migrating to PyScaffold <migration>
   Extending PyScaffold <extensions>
   Embedding PyScaffold <python-api>
   Cookiecutter Integration <cookiecutter-integration>
   Contributions & Help <contributing>
   FAQ <faq>
   License <license>
   Contributors <contributors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _Git: http://git-scm.com/
.. _video tutorial: https://www.youtube.com/watch?v=JwwlRkLKj7o
