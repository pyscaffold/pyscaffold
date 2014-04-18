#!/bin/bash                                                                                                                                           
set -e -x

# Install additional requirements
pip install pytest sphinx

# Setup a test project
PROJECT="my_project"
putup $PROJECT
# Try updating (this does not work on Github)
# DESCRIPTION="new_description"
# putup --update $PROJECT -d $DESCRIPTION
# test `python $PROJECT/setup.py --description` == $DESCRIPTION
# Run some common tasks
cd $PROJECT
python setup.py test
python setup.py docs
python setup.py version
python setup.py sdist
python setup.py bdist
