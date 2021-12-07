#!/usr/bin/env bash

conda install -c conda-forge ffmpeg -y
conda uninstall llvmlite -y # required due to librosa installing llvmlite in 8.0>=
conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=10.2 -c pytorch
pip install -e .
pip install -r requirements.txt