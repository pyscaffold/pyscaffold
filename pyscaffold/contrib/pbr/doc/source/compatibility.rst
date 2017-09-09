..
    The name of this document and the anchor in this document must be
    treated as a stable API.  Links to this document are coded into
    pbr and deployed versions of pbr will refer users to this document
    in the case of certain errors.
    Ensure any link you use in PBR is defined via a ref with .. _name.


===================
Compatibility Notes
===================

Useful notes about errors users may encounter when features cannot be
supported on older versions of setuptools / pip / wheel.


setuptools
==========


.. _evaluate-marker:

evaluate_marker
---------------

evaluate_markers may run into issues with the '>', '>=', '<', and '<='
operators if the installed version of setuptools is less than 17.1.  Projects
using these operators with markers should specify a minimum version of 17.1
for setuptools.


pip
===

markers
-------

For versions of pip < 7 with pbr < 1.9, dependencies that use markers will not
be installed.  Projects using pbr and markers should set a minimum version of
1.9 for pbr.


Recommended setup.py
====================

:ref:`setup_py`.


Sphinx
======

.. _sphinx-1.5:

Version 1.5.0+
--------------

The ``warning-is-error`` flag is only supported by Sphinx 1.5 and will cause
errors when used with older versions.
