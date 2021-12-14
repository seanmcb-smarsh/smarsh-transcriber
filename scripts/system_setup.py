#!/usr/bin/env bash

# Set Local Language
locale-gen en_GB.UTF-8

# Upgrade pip to the latest version.
echo "Install/Update pip3"
sudo apt-get install gcc libpq-dev -y
sudo apt-get install python-dev  python-pip -y
sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y
sudo -H pip3 install --upgrade pip
sudo apt-get install python3-setuptools -y
sudo apt install python3-testresources -y

# Script directory to find the location of requirements.txt
SCRIPT_DIR=$(cd `dirname $0` && pwd)
echo $SCRIPT_DIR


echo "Install Project Dependencies using pip3"
echo "Package setup for delivery"
sudo python3 setup.py sdist bdist_wheel
echo "Install Package"
pip3 install -I dist/transcriber-api*py3-none-any.whl
if [[ $? > 0 ]]
then
  echo "transcriber-api Installation Failed,  existing System Setup."
  exit
else
  echo "transcriber-apil Installation Done."
fi

if [ $? -eq 0 ]
then
	echo "Installation Done"
	echo "System Setup Done"
else
	echo "Installation Failed"
	echo "System Setup Aborted"
fi
