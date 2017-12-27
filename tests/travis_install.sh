#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.
#
# This script is taken from Scikit-Learn (http://scikit-learn.org/)
#

set -e -x

if [[ "${TRAVIS_OS_NAME}" == "osx" ]]; then
    brew outdated || brew update
    brew install gnu-tar

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    case "${PYTHON_VERSION}" in
        2.7)
            curl -O https://bootstrap.pypa.io/get-pip.py
            python get-pip.py --user
            ;;
        3.6)
            brew outdated pyenv || brew upgrade pyenv
            pyenv install 3.6.1
            pyenv global 3.6.1
            ;;
    esac

    pyenv rehash
    python -m pip install --user virtualenv
    virtualenv testenv
    source testenv/bin/activate
fi

if [[ "${DISTRIB}" == "conda" ]]; then
    # Deactivate the travis-provided virtual environment and setup a
    # conda-based environment instead
    deactivate

    # Use the miniconda installer for faster download / install of conda
    # itself
    wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O miniconda.sh
    chmod +x miniconda.sh && ./miniconda.sh -b -p $HOME/miniconda
    export PATH=$HOME/miniconda/bin:$PATH
    conda update --yes conda

    # Configure the conda environment and put it in the path using the
    # provided versions
    conda create -n testenv --yes python=${PYTHON_VERSION} pip virtualenv
    source activate testenv
fi

if [[ "${COVERAGE}" == "true" ]]; then
    pip install -U pytest-cov coverage coveralls flake8
fi

if [[ "${PYTHON_VERSION}" == "2.7" ]]; then
    pip install "django<2.0"
else
    pip install django
fi

# for all
pip install -U pip setuptools
pip install sphinx
pip install cookiecutter
pip install tox
