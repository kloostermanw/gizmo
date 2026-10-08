import os
import sys

# Make the project root importable so tests can `from Commands.branches import Branches`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
