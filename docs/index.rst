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

   pip install -U pip setuptools setuptools_scm
   pip install -e .

.. TODO: Remove the manual installation/update of pip, setuptools and setuptools_scm
   once pip starts supporting editable installs with pyproject.toml

you are all set and ready to go which means in a Python shell you can do the following:

.. code-block:: python

   >>> from my_project.skeleton import fib
   >>> fib(10)
   55

Type ``putup -h`` to learn about more configuration options. PyScaffold assumes
that you have `Git`_ installed and set up on your PC, meaning at least your name
and email are configured.
The project template in ``my_project`` provides you with a lot of
:ref:`features <features>`.

There is also a `video tutorial`_
on how to develop a command-line application with the help of PyScaffold.


.. note::

   PyScaffold 4 is compatible with Python 3.6 and greater
   *(you might be able to run it on Python 3.5, however that is not
   officially supported)*.
   For legacy Python 2.7 please install PyScaffold 2.5
   *(not officially supported)*.


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
   Updating <updating>
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
