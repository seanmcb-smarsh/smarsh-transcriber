#!/usr/bin/env bash
echo "Removing old Build and Packages"
sudo rm -rf vault.egg-info/ build/ dist/
sudo rm -rf /usr/local/lib/python3.8/dist-packages/vault/
sudo rm -rf /usr/local/lib/python3.8/dist-packages/vault-*-py3.8.egg
sudo rm -rf /usr/local/lib/python3.8/dist-packages/vault-*.dist-info/
echo "Packgae setup for offline delivery"
sudo python3 setup.py sdist bdist_wheel
echo "Building Package for offline delivery"
pip3 install -I dist/transcriber-api*py3-none-any.whl
echo "Package Build and Install Completed"