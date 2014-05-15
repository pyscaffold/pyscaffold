#!/bin/bash                                                                                                                                           
set -e -x

# Install additional requirements
pip install sphinx
PROJECT="my_project"
# Delete old project if necessary
if [ -d $PROJECT  ]; then
    rm -rf $PROJECT
fi
# Setup a test project
putup $PROJECT
# Run some common tasks
cd $PROJECT
python setup.py test
python setup.py doctest
python setup.py docs
python setup.py version
python setup.py sdist
python setup.py bdist
# Try updating
cd ..
putup --update $PROJECT
cd $PROJECT
git_diff=`git diff`
test ! -n "$git_diff"
# Try changing the description
cd ..
DESCRIPTION="new_description"
putup --update $PROJECT -d $DESCRIPTION
cd $PROJECT
test "`python setup.py --description`" = $DESCRIPTION
echo "System test successful!"
