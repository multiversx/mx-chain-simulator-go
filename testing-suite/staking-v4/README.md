# Testing suite using mvx python sdk and chain-simulator for staking-v4 feature 

## Overview:
- All tests are written based on scenarios from the internal testing plan.

## How to run: 

### 1) Create a virtual env
`python3 -m venv ./venv`
`source ./venv/bin/activate`

### 2) Install all dependencies 
`pip3 install -r ./req.txt`
 
### 3) Export PythonPath 
`export PYTHONPATH=.`

### 4) Make sure [chain-simulator](https://github.com/multiversx/mx-chain-simulator-go) is:
- Running 
- Running with a correct config (specific config can be found at the begging of every `./scenarios/_test.py`)
- If you run chain-simulator on different port, you can edit it in `./scenarios/config.py`

### 5) RUN
`pytest scenarios/` - to run all scenarios 
`pytest scenarios/_17.py` - to run a specific scenario 

