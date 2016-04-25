"""\
important note:

the setup of setuptools_scm is self-using,
the first execution of `python setup.py egg_info`
will generate partial data
its critical to run `python setup.py egg_info`
once before running sdist or easy_install on a fresh checkouts

pip usage is recommended
"""
from __future__ import print_function
import os
import sys
import setuptools
from setuptools.command.sdist import sdist as sdist_orig


PROBLEMATIC_COMMANDS = 'install', 'develop', 'easy_install', 'bdist_egg'

if not os.path.isdir('setuptools_scm.egg-info'):
    print(__doc__)

    if any(c in sys.argv for c in PROBLEMATIC_COMMANDS):
        sys.exit('please run `python setup.py egg_info` first')


def scm_config():
    from setuptools_scm.version import (
        guess_next_dev_version,
        get_local_node_and_date,
    )
    return dict(
        version_scheme=guess_next_dev_version,
        local_scheme=get_local_node_and_date,
    )

with open('README.rst') as fp:
    long_description = fp.read()


class sdist(sdist_orig):
    def make_release_tree(self, base_dir, files):
        sdist_orig.make_release_tree(self, base_dir, files)
        target = os.path.join(base_dir, 'setup.py')
        with open(__file__) as fp:
            template = fp.read()
        ver = self.distribution.version
        if not ver:
            from setuptools_scm import get_version
            ver = get_version(**scm_config())

        finalized = template.replace(
            'use_scm_version=scm_config,\n',
            'version="%s",\n' % ver)
        os.remove(target)
        with open(target, 'w') as fp:
            fp.write(finalized)


arguments = dict(
    name='setuptools_scm',
    url='https://github.com/pypa/setuptools_scm/',
    zip_safe=True,
    # pass here since entrypints are not yet registred
    use_scm_version=scm_config,
    author='Ronny Pfannschmidt',
    author_email='opensource@ronnypfannschmidt.de',
    description=('the blessed package to manage your versions by scm tags'),
    long_description=long_description,
    license='MIT',
    packages=[
        'setuptools_scm',
    ],
    entry_points="""
        [distutils.setup_keywords]
        use_scm_version = setuptools_scm.integration:version_keyword

        [setuptools.file_finders]
        setuptools_scm = setuptools_scm.integration:find_files

        [setuptools_scm.parse_scm]
        .hg = setuptools_scm.hg:parse
        .git = setuptools_scm.git:parse

        # those are left here for backward compatibility in the 1.x series
        .hg_archival.txt = setuptools_scm.hg:parse_archival
        PKG-INFO = setuptools_scm.hacks:parse_pkginfo

        [setuptools_scm.parse_scm_fallback]
        .hg_archival.txt = setuptools_scm.hg:parse_archival
        PKG-INFO = setuptools_scm.hacks:parse_pkginfo

        [setuptools_scm.files_command]
        .hg = setuptools_scm.hg:FILES_COMMAND
        .git = setuptools_scm.git:FILES_COMMAND

        [setuptools_scm.version_scheme]
        guess-next-dev = setuptools_scm.version:guess_next_dev_version
        post-release = setuptools_scm.version:postrelease_version

        [setuptools_scm.local_scheme]
        node-and-date = setuptools_scm.version:get_local_node_and_date
        dirty-tag = setuptools_scm.version:get_local_dirty_tag
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
    ],
    cmdclass={'sdist': sdist}
)

if __name__ == '__main__':
    setuptools.setup(**arguments)
