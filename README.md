[![Build Status](https://travis-ci.org/bdmccord/simoc.svg?branch=master)](https://travis-ci.org/bdmccord/simoc)

# SIMOC

## ASU SER-401 Capstone Team 15

SIMOC - A Scalable Model of an Isolated, Off-world Community

## Getting Started
***Note***: *SIMOC is incompatible with python 2.x, python 3 must be used due to its dependency on the mesa framework.  Depending on the configuration of your system you may need to  replace "python" with python3 where necessary. If using anaconda see [these instructions](https://conda.io/docs/user-guide/tasks/manage-python.html) to set up a python 3 environment.*

### Setup

#### Clone Repository
`git clone --recursive https://github.com/kstaats/simoc.git`

#### Install dependencies:

`pip install -r requirements.txt`

#### Create Database

`python create_db.py`

### Running Server

#### Normal Run

`python -m simoc_server`

#### Debug Mode
`python -m simoc_server --debug`

#### Specify Port
`python -m simoc_server --port 9000`

#### Run Locally
`python -m simoc_server --run_local`

#### Run using JSON Serialization For API Testing
`python -m simoc_server --use_json`

### Testing
`python run_tests.py`
