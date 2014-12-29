#!/bin/bash
set -e -x

PROJECT="my_project"
# Delete old project if necessary
if [ -d ${PROJECT}  ]; then
    rm -rf ${PROJECT}
fi

function run_common_tasks {
    cd ${PROJECT}
    python setup.py test
    python setup.py doctest
    python setup.py docs
    python setup.py version
    python setup.py sdist
    python setup.py bdist
    cd ..
}

# Setup a test project
putup ${PROJECT}
# Run some common tasks
run_common_tasks
# Try updating
putup --update ${PROJECT}
cd ${PROJECT}
git_diff=`git diff`
test ! -n "$git_diff"
# Try changing the description
cd ..
DESCRIPTION="new_description"
putup --force --update ${PROJECT} -d ${DESCRIPTION}
cd ${PROJECT}
test "`python setup.py --description`" = ${DESCRIPTION}
cd ..
# Try forcing overwrite
putup --force --with-tox ${PROJECT}
# Try running Tox
if [[ "${DISTRIB}" == "ubuntu" ]]; then
    cd ${PROJECT}
    tox -e py27
    cd ..
fi
# Try all kinds of --with options
rm -rf ${PROJECT}
if [[ "${DISTRIB}" == "ubuntu" ]]; then
    putup --with-numpydoc ${PROJECT}
    run_common_tasks
    rm -rf ${PROJECT}
fi
putup --with-django ${PROJECT}
run_common_tasks
rm -rf ${PROJECT}
putup --with-pre-commit ${PROJECT}
run_common_tasks
rm -rf ${PROJECT}
putup --with-travis ${PROJECT}
run_common_tasks
# Test update from PyScaffold version < 2.0
if [[ "${DISTRIB}" == "ubuntu" ]]; then
    git clone --branch v0.2 https://github.com/blue-yonder/pydse.git
    putup --update pydse
    cd pydse
    run_common_tasks
fi

echo "System test successful!"
