#!/bin/sh -e

export VERSION_SCRIPT="import sys; print('%s.%s' % sys.version_info[0:2])"
export PYTHON_VERSION=`python -c "$VERSION_SCRIPT"`
export PYTHONPATH=.

set -x
pip install pytest

python3 -m pytest -W ignore::DeprecationWarning -o junit_family=xunit2 --junitxml=pytest-report.xml --cov-report term-missing --cov=asr tests --durations=10

python3 -m coverage xml -i