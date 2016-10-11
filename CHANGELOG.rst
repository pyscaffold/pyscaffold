v1.13.1
=======

* fix issue #86 - detect dirty git workdir without tags

v1.13.0
=======

* fix regression caused by the fix of #101
  * assert types for version dumping
  * strictly pass all versions trough parsed version metadata

v1.12.0
=======

* fix issue #97 - add support for mercurial plugins
* fix issue #101 - write version cache even for pretend version
  (thanks anarcat for reporting and fixing)

v1.11.1
========

* fix issue #88 - better docs for sphinx usage (thanks Jason)
* fix issue #89 - use normpath to deal with windows
  (thanks Te-jé Rodgers for reporting and fixing)

v1.11.0
=======

* always run tag_to_version so in order to handle prefixes on old setuptools
  (thanks to Brian May)
* drop support for python 3.2
* extend the error message on missing scm metadata
  (thanks Markus Unterwaditzer)
* fix bug when using callable version_scheme
  (thanks Esben Haabendal)

v1.10.1
=======

* fix issue #73 - in hg pre commit merge, consider parent1 instead of failing

v1.10.0
=======

* add support for overriding the version number via the
  environment variable SETUPTOOLS_SCM_PRETEND_VERSION

* fix isssue #63 by adding the --match parameter to the git describe call
  and prepare the possibility of passing more options to scm backends

* fix issue #70 and #71 by introducing the parse keyword
  to specify custom scm parsing, its an expert feature,
  use with caution

  this change also introduces the setuptools_scm.parse_scm_fallback
  entrypoint which can be used to register custom archive fallbacks


v1.9.0
======

* Add :code:`relative_to` parameter to :code:`get_version` function;
  fixes #44 per #45.

v1.8.0
======

* fix issue with setuptools wrong version warnings being printed to standard
  out. User is informed now by distutils-warnings.
* restructure root finding, we now reliably ignore outer scm
  and prefer PKG-INFO over scm, fixes #43 and #45

v1.7.0
======

* correct the url to github
  thanks David Szotten
* enhance scm not found errors with a note on git tarballs
  thanks Markus
* add support for :code:`write_to_template`

v1.6.0
======

* bail out early if the scm is missing

  this brings issues with git tarballs and
  older devpi-client releases to light,
  before we would let the setup stay at version 0.0,
  now there is a ValueError

* propperly raise errors on write_to missuse (thanks Te-jé Rodgers)

v1.5.5
======

* Fix bug on Python 2 on Windows when environment has unicode fields.

v1.5.4
======

* Fix bug on Python 2 when version is loaded from existing metadata.

v1.5.3
======

* #28: Fix decoding error when PKG-INFO contains non-ASCII.

v1.5.2
======

* add zip_safe flag

v1.5.1
======

* fix file access bug i missed in 1.5

v1.5.0
======

* moved setuptools integration related code to own file
* support storing version strings into a module/text file
  using the :code:`write_to` coniguration parameter

v1.4.0
======

* propper handling for sdist
* fix file-finder failure from windows
* resuffle docs

v1.3.0
======

* support setuptools easy_install egg creation details
  by hardwireing the version in the sdist

v1.2.0
======

* enhance self-use

v1.1.0
======

* enable self-use

v1.0.0
======

* documentation enhancements

v0.26
=====

* rename to setuptools_scm
* split into package, add lots of entry points for extension
* pluggable version schemes

v0.25
=====

* fix pep440 support
  this reshuffles the complete code for version guessing

v0.24
=====

* dont drop dirty flag on node finding
* fix distance for dirty flagged versions
* use dashes for time again,
  its normalisation with setuptools
* remove the own version attribute,
  it was too fragile to test for
* include file finding
* handle edge cases around dirty tagged versions

v0.23
=====

* windows compatibility fix (thanks stefan)
  drop samefile since its missing in
  some python2 versions on windows
* add tests to the source tarballs


v0.22
=====

* windows compatibility fix (thanks stefan)
  use samefile since it does path normalisation

v0.21
=====

* fix the own version attribute (thanks stefan)

v0.20
=====

* fix issue 11: always take git describe long format
  to avoid the source of the ambiguity
* fix issue 12: add a __version__ attribute via pkginfo

v0.19
=====

* configurable next version guessing
* fix distance guessing (thanks stefan)
