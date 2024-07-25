#!/bin/bash

sudo apt update
sudo apt install python3-pip
python3 -m pip install --upgrade pip
cd ../..
pip3 install -r examples/requirements.txt
pip3 install pytest
