# SIMOC
`SIMOC` - A Scalable, Interactive Model of an Off-world Community

## Getting Started

Depending on your use case, infrastructure and environment,
you can choose out of multiple deployment scenarios supported by `SIMOC`.

Please use the corresponding guide based on your set up:
- [Run SIMOC locally on Linux/macOS using Docker (recommended)](https://simoc.space/docs/user_guide/developer/docker-deployment.html)
- [Manually install and run SIMOC locally (without Docker)](https://simoc.space/docs/user_guide/developer/local-deployment.html)
- [Deploy SIMOC to Google Kubernetes Engine](https://simoc.space/docs/user_guide/developer/gcp-deployment.html)

## Jupyter Workflow

A Jupyter Notebook is included, `Custom_Agent_Template.ipynb`, which
demonstrates the command-line usage of the SIMOC Agent Model.

To setup the Jupyter environment:
```
pip install -r requirements-jupyter.txt
jupyter notebook
```
