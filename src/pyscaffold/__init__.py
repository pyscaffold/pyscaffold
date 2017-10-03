import pkg_resources

from .contrib import setuptools_scm

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
