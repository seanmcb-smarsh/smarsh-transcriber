#!/bin/bash
set -eux pipefail

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
chmod +x  ~/miniconda.sh
mkdir -p /users/$USER/tmpconda
TMPDIR=/users/$USER/tmpconda bash ~/miniconda.sh -b -p $HOME/miniconda
echo 'export PATH="/home/$USER/miniconda/bin:$PATH"' | sudo tee -a .bashrc
echo "MiniConda Installation completed"
source ~/.bashrc
echo "Installing PyTorch"
conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=10.2 -c pytorch
echo "PyTorch Installation completed"
echo "Installing CudaToolKit"
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-ubuntu1604.pin
sudo mv cuda-ubuntu1604.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.2.1/local_installers/cuda-repo-ubuntu1604-11-2-local_11.2.1-460.32.03-1_amd64.deb -O ~/nvidia_cuda.deb
sudo dpkg -i ~/nvidia_cuda.deb
sudo apt-key add /var/cuda-repo-ubuntu1604-11-2-local/7fa2af80.pub
sudo apt-get update
sudo apt-get -y install cuda
echo "CudaToolKit Installation completed"