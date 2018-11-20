#!/bin/bash

set -e -x

# Compile wheels
PYTHON="/opt/python/${PYTHON_VERSION}/bin/python"
PIP="/opt/python/${PYTHON_VERSION}/bin/pip"
${PIP} install --upgrade pip setuptools wheel~=0.31.1
${PIP} install -r /io/.ci/requirements.txt
rm -rf /io/build
${PIP} wheel /io/ -w /io/dist/

# Bundle external shared libraries into the wheels.
for whl in /io/dist/*.whl; do
    auditwheel repair $whl -w /io/dist/
    rm /io/dist/*-linux_*.whl
done

# Grab docker host, where Postgres should be running.
export PGHOST=$(ip route | awk '/default/ { print $3 }' | uniq)
export PGUSER="postgres"

PYTHON="/opt/python/${PYTHON_VERSION}/bin/python"
PIP="/opt/python/${PYTHON_VERSION}/bin/pip"
${PIP} install ${PYMODULE} --no-index -f file:///io/dist
rm -rf /io/tests/__pycache__
"${PYTHON}" /io/tests/__init__.py
rm -rf /io/tests/__pycache__
