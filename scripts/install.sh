#!/bin/sh -e

# Use the Python executable provided from the `-p` option, or a default.
[ "$1" = "-p" ] && PYTHON="python3"

REQUIREMENTS="requirements.txt"
VENV="venv"
PIP="pip3"

set -x

if [ -z "$GITHUB_ACTIONS" ]; then
    REQUIREMENTS="requirements/dev.txt"
else
    PIP="pip3"
fi

conda install -c conda-forge ffmpeg -y
conda install -y pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=10.2 -c pytorch

"$PIP" install -r "$REQUIREMENTS"
"$PIP" install -e .
