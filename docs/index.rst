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
template* [#index1]_ with everything you need for some serious coding. Checkout out
`this demo project`_, which was set up using Pyscaffold.

.. note::
   .. versionadded:: 4.0
      The **experimental** [#index2]_ "interactive mode" makes it easy to choose
      which options you want to pass to PyScaffold. If you want to try it out,
      you can use the ``--interactive``, or simply ``-i`` option.
      The interactive command equivalent to the previous example is:
      ``putup -i myproject``.

To be able to interact with your project and call its functions from the
command line, you can run the usual [#index3]_:

.. code-block:: shell

   cd my_project
   pip install -e .

You are then all set and ready to go which means in a Python shell you can do
the following [#index4]_:

.. code-block:: pycon

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


.. [#index1] PyScaffold's project template makes use of a dedicated ``src``
   folder to store all the package files meant for distribution (additional
   files like tests and documentation are kept in their own separated folders).
   You can find some comments and useful links about this design decision in
   our :ref:`FAQ <faq>`.


.. [#index2] Experimental features in PyScaffold are not considered stable
   and can change the way they work (or even be removed) between any releases.
   If you are scripting with PyScaffold, please avoid using them.


.. [#index3] This command installs your project in |editable mode|_, making it
   available in import statements as any other Python module.
   It might fail if your have an old version of Python's package manager and
   tooling in your current environment. Please make sure you are using the
   intended environment (either a `virtual environment`_ [*recommended*] or the
   default installation of Python in the operating system) and try to update
   them with ``python -m pip install -U pip setuptools``.


.. [#index4] If you are using a `virtual environment`_, please remember to
   re-activate it everytime you close your shell, otherwise you will not be
   able to import your project in the REPL_. To check if you have already
   activated it you can run ``which python`` on Linux and OSX, ``where python``
   on the classical Windows command prompt, or ``Get-Command python`` on
   PowerShell.

.. |editable mode| replace:: *"editable mode"*

.. _Git: http://git-scm.com/
.. _video tutorial: https://www.youtube.com/watch?v=JwwlRkLKj7o
.. _this demo project: https://github.com/pyscaffold/pyscaffold-demo
.. _editable mode: https://pip.pypa.io/en/stable/reference/pip_install/#install-editable
.. _REPL: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
