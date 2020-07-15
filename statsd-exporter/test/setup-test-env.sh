#!/bin/bash
set -xe
rm -rf ./venv
virtualenv --python=python3 --always-copy ./venv
./venv/bin/pip install -r ./requirements.txt
set +x
echo "============================"
echo ""
echo "Please run:"
echo "source ./venv/bin/activate"
echo ""
echo "Then you can run:"
echo "pytest test.py"
echo "============================"
