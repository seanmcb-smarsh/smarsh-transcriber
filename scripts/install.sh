#!/bin/sh -e

# Use the Python executable provided from the `-p` option, or a default.
[ "$1" = "-p" ] && PYTHON="python3"

REQUIREMENTS="requirements.txt"
VENV="venv"

conda install -c conda-forge ffmpeg -y
conda uninstall llvmlite -y # required due to librosa installing llvmlite in 8.0>=
conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=10.2 -c pytorch

set -x

if [ -z "$GITHUB_ACTIONS" ]; then
    "$PYTHON" -m venv "$VENV"
    PIP="$VENV/bin/pip"
else
    PIP="pip3"
fi

"$PIP" install -r "$REQUIREMENTS"
"$PIP" install -e .
