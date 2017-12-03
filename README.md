# SIMOC

## ASU SER-401 Capstone Team 15

SIMOC - A Scalable Model of an Isolated, Off-world Colony

- This is the server side backend for SIMOC, to view the client [click here](https://github.com/gschober/simoc_client)

## Getting Started

### Setup

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
