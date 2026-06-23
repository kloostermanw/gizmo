#!/bin/bash

# Create directory
mkdir -p ~/venvs/gizmo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd ~/venvs/gizmo
python3 -m venv venv/
source venv/bin/activate
pip3 install -r "$SCRIPT_DIR/requirements.txt"

deactivate
echo "Run your program with:"
echo "~/venvs/gizmo/venv/bin/python /path/to/gizmo"