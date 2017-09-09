===============================
 Notes for Package maintainers
===============================

If you are maintaining packages of software that uses `pbr`, there are some
features you probably want to be aware of that can make your life easier.
They are exposed by environment variables, so adding them to rules or spec
files should be fairly easy.

Versioning
==========

`pbr`, when run in a git repo, derives the version of a package from the
git tags. When run in a tarball with a proper egg-info dir, it will happily
pull the version from that. So for the most part, the package maintainers
shouldn't need to care. However, if you are doing something like keeping a
git repo with the sources and the packaging intermixed and it's causing pbr
to get confused about whether its in its own git repo or not, you can set
`PBR_VERSION`:

::

  PBR_VERSION=1.2.3

and all version calculation logic will be completely skipped and the supplied
version will be considered absolute.

Distribution version numbers
============================

`pbr` will automatically calculate upstream version numbers for dpkg and rpm
using systems. Releases are easy (and obvious). When packaging preleases though
things get more complex. Firstly, semver does not provide for any sort order
between pre-releases and development snapshots, so it can be complex (perhaps
intractable) to package both into one repository - we recommend with either
packaging pre-release releases (alpha/beta/rc's) or dev snapshots but not both.
Secondly, as pre-releases and snapshots have the same major/minor/patch version
as the version they lead up to, but have to sort before it, we cannot map their
version naturally into the rpm version namespace: instead we represent their
versions as versions of the release before.

Dependencies
============

As of 1.0.0 `pbr` doesn't alter the dependency behaviour of `setuptools`.

Older versions would invoke `pip` internally under some circumstances and
required the environment variable `SKIP_PIP_INSTALL` to be set to prevent
that. Since 1.0.0 we now document that dependencies should be installed before
installing a `pbr` using package. We don't support easy install, but neither
do we interfere with it today. If you observe easy install being triggered when
building a binary package, then you've probably missed one or more package
requirements.

Note: we reserve the right to disable easy install via `pbr` in future, since
we don't want to debug or support the interactions that can occur when using
it.

Tarballs
========

`pbr` includes everything in a source tarball that is in the original `git`
repository. This can again cause havoc if a package maintainer is doing fancy
things with combined `git` repos, and is generating a source tarball using
`python setup.py sdist` from that repo. If that is the workflow the packager
is using, setting `SKIP_GIT_SDIST`:

::

  SKIP_GIT_SDIST=1

will cause all logic around using git to find the files that should be in the
source tarball to be skipped. Beware though, that because `pbr` packages
automatically find all of the files, most of them do not have a complete
`MANIFEST.in` file, so its possible that a tarball produced in that way will
be missing files.

AUTHORS and ChangeLog
=====================

`pbr` generates AUTHORS and ChangeLog files from git information. This
can cause problem in distro packaging if package maintainer is using git
repository for packaging source. If that is the case setting
`SKIP_GENERATE_AUTHORS`

::

   SKIP_GENERATE_AUTHORS=1

will cause logic around generating AUTHORS using git information to be
skipped. Similarly setting `SKIP_WRITE_GIT_CHANGELOG`

::

   SKIP_WRITE_GIT_CHANGELOG=1

will cause logic around generating ChangeLog file using git
information to be skipped.
