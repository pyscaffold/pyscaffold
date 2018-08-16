# -*- coding: utf-8 -*-

"""
Integration part for hooking into distutils/setuptools

Rationale:
The ``use_pyscaffold`` keyword is unknown to setuptools' setup(...) command,
therefore the ``entry_points`` are checked for a function to handle this
keyword which is ``pyscaffold_keyword`` below. This is where we hook into
setuptools and apply the magic of setuptools_scm as well as other commands.
"""
from distutils.cmd import Command

from .contrib import ptr
from .contrib.setuptools_scm.integration import version_keyword
from .repo import get_git_root
from .utils import check_setuptools_version


def version2str(version):
    """Creates a PEP440 version string

    Args:
        version (:obj:`setuptools_scm.version.ScmVersion`): version object

    Returns:
        str: version string
    """
    if version.exact or not version.distance > 0:
        return version.format_with('{tag}')
    else:
        distance = version.distance
        version = str(version.tag)
        if '.dev' in version:
            version, tail = version.rsplit('.dev', 1)
            assert tail == '0', 'own dev numbers are unsupported'
        return '{}.post0.dev{}'.format(version, distance)


def local_version2str(version):
    """Create the local part of a PEP440 version string

    Args:
        version (:obj:`setuptools_scm.version.ScmVersion`): version object

    Returns:
        str: local version
    """
    if version.exact:
        return ''
    else:
        if version.dirty:
            return version.format_with('+{node}.dirty')
        else:
            return version.format_with('+{node}')


def setuptools_scm_config(value):
    """Generate the configuration for setuptools_scm

    Args:
        value: value from entry_point

    Returns:
        dict: dictionary of options
    """
    value = value if isinstance(value, dict) else dict()
    value.setdefault('root', get_git_root(default='.'))
    value.setdefault('version_scheme', version2str)
    value.setdefault('local_scheme', local_version2str)
    return value


def build_cmd_docs():
    """Return Sphinx's BuildDoc if available otherwise a dummy command

    Returns:
        :obj:`~distutils.cmd.Command`: command object
    """
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx
    else:
        return BuildDoc


def pyscaffold_keyword(dist, keyword, value):
    """Handles the `use_pyscaffold` keyword of the setup(...) command

    Args:
        dist (:obj:`setuptools.dist`): distribution object as
        keyword (str): keyword argument = 'use_pyscaffold'
        value: value of the keyword argument
    """
    check_setuptools_version()
    if value:
        version_keyword(dist, keyword, setuptools_scm_config(value))
        dist.cmdclass['docs'] = build_cmd_docs()
        dist.cmdclass['doctest'] = build_cmd_docs()
        dist.cmdclass['build_sphinx'] = build_cmd_docs()
        dist.command_options['doctest'] = {'builder': ('setup.py', 'doctest')}
        dist.cmdclass['test'] = ptr.PyTest
