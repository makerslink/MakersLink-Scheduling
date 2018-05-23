#!/bin/bash
if [ ! -d "./virtenv" ]; then
    virtualenv ./virtenv --python=python3
fi
echo "Entering virtualenv - hopefully you typed 'source ./start-env.sh'"
source ./virtenv/bin/activate
