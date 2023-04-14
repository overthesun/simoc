# SIMOC
`SIMOC` - A Scalable, Interactive Model of an Off-world Community

## Getting Started

You can follow the [Setting up SIMOC](https://simoc.space/docs/user_guide/developer/setup.html)
documentation page, in particular:
* [setup instructions for users](https://simoc.space/docs/user_guide/developer/setup.html#for-simoc-users)
* [setup instructions for developers](https://simoc.space/docs/user_guide/developer/setup.html#for-simoc-developers)

See also [the repository setup instructions](https://simoc.space/docs/user_guide/developer/git.html#repo-setup).

The documentation also includes other possible options (some of which are no longer supported):
- [Deploy SIMOC to Google Kubernetes Engine](https://simoc.space/docs/user_guide/developer/gcp-deployment.html)
- [Manually install and run SIMOC locally without Docker (possibly outdated)](https://simoc.space/docs/user_guide/developer/local-deployment.html)
<!-- - [Run SIMOC locally on Linux/macOS using Docker (outdated)](https://simoc.space/docs/user_guide/developer/docker-deployment.html) -->

## Jupyter Workflow

A Jupyter Notebook is included, `Custom_Agent_Template.ipynb`, which
demonstrates the command-line usage of the SIMOC Agent Model.

To setup the Jupyter environment:
```
pip install -r requirements-jupyter.txt
jupyter notebook
```
