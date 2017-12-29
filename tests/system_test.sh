#!/bin/bash
set -e -x

WORKSPACE=`pwd`
# Change into temporary directory since we want to be outside of git
cd /tmp

function cleanup {
    if [ -d ${1} ]; then
        rm -rf ${1}
    fi
}

function run_common_tasks {
    cd ${1}

    if [[ "${2}" != "no_tests" && "${3}" != "no_tests" ]]; then
        python setup.py test
    fi

    python setup.py doctest
    python setup.py docs
    python setup.py --version
    python setup.py sdist
    python setup.py bdist
    if [[ "${COVERAGE}" == "true" && "${2}" != "no_flake8" ]]; then
        echo "Checking code style with flake8..."
        flake8 --count
    fi
    cd ..
}

PROJECT="my_project"
cleanup ${PROJECT}

# Setup a test project
putup ${PROJECT}
# Run some common tasks
run_common_tasks ${PROJECT}
# Try updating
putup --update ${PROJECT}
cd ${PROJECT}
git_diff=`git diff`
test ! -n "$git_diff"
# Try different project name than package name
putup MY_COOL_PROJECT -p ${PROJECT}
run_common_tasks MY_COOL_PROJECT
cleanup MY_COOL_PROJECT
# Try forcing overwrite
putup --force --tox ${PROJECT}
# Try running Tox
if [[ "${DISTRIB}" == "ubuntu" ]]; then
    cd ${PROJECT}
    tox -e ${TOX_PYTHON_VERSION}
    cd ..
fi
# Try all kinds of extensions
cleanup ${PROJECT}
putup --django ${PROJECT}
run_common_tasks ${PROJECT} "no_flake8"
cleanup ${PROJECT}
putup --pre-commit ${PROJECT}
run_common_tasks ${PROJECT}
cleanup ${PROJECT}
putup --travis ${PROJECT}
run_common_tasks ${PROJECT}
cleanup ${PROJECT}
putup --gitlab ${PROJECT}
run_common_tasks ${PROJECT}
cleanup ${PROJECT}
putup --no-skeleton ${PROJECT}
run_common_tasks ${PROJECT} "no_tests"

# Test Makefile for sphinx
PROJECT="project_with_docs"
cleanup ${PROJECT}
putup  ${PROJECT}
cd ${PROJECT}/docs
PYTHONPATH=.. make html

# Test update from PyScaffold version 2.0
if [[ "${DISTRIB}" == "conda" && "${PYTHON_VERSION}" == "2.7" ]]; then
    TMPDIR="update_test"
    mkdir ${TMPDIR}; cd ${TMPDIR}
    git clone --branch v0.2.1 https://github.com/blue-yonder/pydse.git pydse
    cp ${TRAVIS_BUILD_DIR}/tests/misc/pydse_setup.cfg pydse/setup.cfg
    putup --update pydse
    conda install --yes nomkl numpy scipy matplotlib libgfortran
    pip install -v -r pydse/requirements.txt
    run_common_tasks pydse
    cd ..
    rm -rf ${TMPDIR}
fi

# Test namespace package
PROJECT="nested_project"
PACKAGE="my_package"
cleanup ${PROJECT}

putup ${PROJECT} -p ${PACKAGE} --namespace com.blue_yonder
run_common_tasks ${PROJECT}

# Test if update remembers extensions
putup ${PROJECT} --update
if [ -d "${PROJECT}/src/${PACKAGE}" ]; then
  echo "Package should still be nested after update, but it is not!"
  exit 1
fi

# Test if update allows adding extensions
putup ${PROJECT} --update --travis
if [ ! -e "${PROJECT}/.travis.yml" ]; then
  echo "Update should have created travis files"
  exit 1
fi


# Test namespace package without skeleton
cleanup ${PROJECT}

putup ${PROJECT} -p my_package --namespace com.blue_yonder --no-skeleton
run_common_tasks ${PROJECT} "no_tests"
if [ -e "${PROJECT}/src/com/blue_yonder/my_package/skeleton.py" ]; then
  echo "File skeleton.py should not exist!"
  exit 1
fi
cleanup ${PROJECT}

# Test namespace + cookiecutter
COOKIECUTTER_URL="https://github.com/FlorianWilhelm/cookiecutter-pypackage.git"
PROJECT="cookiecutter_nested_project"
# Delete old project if necessary
cleanup ${PROJECT}
echo ${COOKIECUTTER_URL}

putup ${PROJECT} --namespace nested.ns \
  --cookiecutter ${COOKIECUTTER_URL}
run_common_tasks ${PROJECT} "no_flake8" "no_tests"

if [ -d "${PROJECT}/src/${PROJECT}" ]; then
  echo "Package should be nested, but it is not!"
  exit 1
fi

# THIS CURRENTLY DEACTIVATED SINCE COOKIECUTTER DOES NOT PLAY NICE WITH US
## Test that update remembers extensions from creation time
#putup ${PROJECT} --update
#if [ -d "${PROJECT}/src/${PROJECT}" ]; then
#  echo "Package should be nested after update, but it is not!"
#  exit 1
#fi
## Test that update allows adding new extensions
#putup ${PROJECT} --update --travis
#if [ ! -e "${PROJECT}/.travis.yml" ]; then
#  echo "Update should have created travis files"
#  exit 1
#fi
cleanup ${PROJECT}

echo "System test successful!"
cd ${WORKSPACE}

if [[ "${COVERAGE}" == "true" ]]; then
    echo "Checking code style with flake8..."
    flake8 --count
fi
echo "All done..."
