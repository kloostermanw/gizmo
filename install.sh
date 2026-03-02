#!/bin/bash

# Create directory
mkdir -p ~/venvs/gizmo

cd ~/venvs/gizmo
python3 -m venv venv/
source venv/bin/activate
pip3 install gitpython

deactivate
echo "Run your program with:"
echo "~/venvs/gizmo/venv/bin/python /path/to/gizmo"