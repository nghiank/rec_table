#!/bin/bash
TENSORFLOW_PATH="/opt/python/current/app/tensorflow"
if [ ! -d  $TENSORFLOW_PATH ]; then
    mkdir $TENSORFLOW_PATH
fi
virtualenv --system-site-packages -p python3 $TENSORFLOW_PATH 
source /opt/python/current/app/tensorflow/bin/activate
pip3 install --upgrade tensorflow
pip3 install Pillow