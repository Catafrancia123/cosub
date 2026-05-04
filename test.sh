#!/bin/bash
PYTHON_VERSION=$(python3 --version | sed -E 's/^Python ([0-9]+\.[0-9]+?).*/\1/')
echo $PYTHON_VERSION
