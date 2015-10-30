import os
os.environ['SETUPTOOLS_SCM_DEBUG'] = '1'
VERSION_PKGS = ['setuptools', 'setuptools_scm']


def pytest_report_header():
    import pkg_resources
    res = []
    for pkg in VERSION_PKGS:
        version = pkg_resources.get_distribution(pkg).version
        res.append('%s version %s' % (pkg, version))
    return res
