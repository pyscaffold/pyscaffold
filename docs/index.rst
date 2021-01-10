.. image:: gfx/logo.png
   :height: 512px
   :width: 512px
   :scale: 60 %
   :alt: PyScaffold logo
   :align: center

|

PyScaffold is the tool of choice for bootstrapping high quality Python
packages, ready to be shared on PyPI_ and installed via pip_.
It is easy to use and encourages the adoption of the best tools and
practices of the Python ecosystem, helping you (and your team, if your have one)
to stay sane, happy and productive. The best part? It is stable and been used
in the wild for over half a decade!

.. _get started:

One command is all it takes to quickly start coding like a Python rockstar
and skip all the difficult and tedious bits::

    putup your_project_name

This will create a new folder called ``your_project_name`` containing a
*perfect project template* [#index1]_ with everything you need for getting things done.
Checkout out `this demo project`_, which was set up using Pyscaffold.

.. tip::
   .. versionadded:: 4.0
      We are trying out a brand new *interactive mode* [#index2]_ that makes it
      even easier to use PyScaffold in its full potential.
      If you want to give it a shot, use the ``--interactive``, or simply ``-i`` option.

      The interactive command equivalent to the previous example is:
      ``putup -i your_project_name``.

You can ``cd`` into your new project and interact with it from the
command line after the usual editable install [#index3]_::

   pip install -e .

… all set and ready to go! Try the following in a Python shell [#index4]_:

.. code-block:: pycon

   >>> from your_project_name.skeleton import fib
   >>> fib(10)
   55

Or if you are concerned about performing package maintainer tasks, make sure to
have tox_ installed and see what we have prepared for you out of the box::

   tox -e docs  # to build your documentation
   tox -e build  # to build your package distribution
   tox -e publish  # to test your project uploads correctly in test.pypi.org
   tox -e publish -- --repository pypi  # to release your package to PyPI
   tox -av  # to list all the tasks available

Type ``putup -h`` to learn about ref:`other things PyScaffold can do <features>`_ for your project,
and if you are not convinced yet, have a look on these :ref:`reasons to use PyScaffold <reasons>`_

There is also a `video tutorial`_ on how to develop a command-line application with the help of PyScaffold.


.. note::

   PyScaffold 4 is compatible with Python 3.6 and greater
   For legacy Python 2.7 please install PyScaffold 2.5
   *(not officially supported)*.


Contents
--------

.. toctree::
   :maxdepth: 2

   Why PyScaffold? <reasons>
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


.. [#index2] Experimental features can change the way they work (or be removed)
   between any releases. If you are scripting with PyScaffold, please avoid using them.


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

.. _PyPI: https://pypi.org/
.. _pip: https://pip.pypa.io/
.. _video tutorial: https://www.youtube.com/watch?v=JwwlRkLKj7o
.. _this demo project: https://github.com/pyscaffold/pyscaffold-demo
.. _editable mode: https://pip.pypa.io/en/stable/reference/pip_install/#install-editable
.. _REPL: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
