#!/bin/bash
TENSORFLOW_PATH=/tmp/tensorflow
if [ ! -d  $TENSORFLOW_PATH ]; then
    mkdir $TENSORFLOW_PATH
fi
python3 -m venv --system-site-packages $TENSORFLOW_PATH 
source $TENSORFLOW_PATH/bin/activate