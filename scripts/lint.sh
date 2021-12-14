#!/bin/sh -e

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}mypy vault --ignore-missing-imports --disallow-untyped-defs
${PREFIX}autoflake --in-place --recursive vault tests setup.py
${PREFIX}black vault tests setup.py
${PREFIX}isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --apply vault tests setup.py
${PREFIX}mypy vault --ignore-missing-imports --disallow-untyped-defs