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
putup --update ${PROJECT} -d ${DESCRIPTION}
cd ${PROJECT}
test "`python setup.py --description`" = ${DESCRIPTION}
cd ..
putup --force --update ${PROJECT} -d ${DESCRIPTION}
cd ${PROJECT}
test "`python setup.py --description`" = ${DESCRIPTION}
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
putup --with-junit-xml --with-coverage-xml --with-coverage-html ${PROJECT}
run_common_tasks
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
echo "System test successful!"
