#!/bin/bash
echo "Hopefully you typed 'source ./stop-env.sh'"

pip3 freeze > reqirements.txt
deactivate
