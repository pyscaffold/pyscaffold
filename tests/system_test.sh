#!/bin/bash                                                                                                                                           
set -e -x

# Install additional requirements
pip install pytest sphinx

# Setup a test project
PROJECT="my_project"
putup $PROJECT
# Run some common tasks
cd $PROJECT
python setup.py test
python setup.py docs
python setup.py version
python setup.py sdist
python setup.py bdist
# Try updating
cd ..
DESCRIPTION="new_description"
putup --update $PROJECT -d $DESCRIPTION
cd $PROJECT
test `python setup.py --description` == $DESCRIPTION
