<!--
Note: this file is a .md for two reasons:
1. so that it doesn't get included by Sphinx
2. so that it shows up directly on GitHub
-->

# SIMOC Documentation

This document explains how to set up Sphinx and use it to build the
documentation.  For the actual SIMOC documentation, you can either browse
the individual doc files on GitHub, or build the documentation locally.


## Initial setup

SIMOC documentation is built using Sphinx.  In order to build the documentation
locally, you will need to install `python3-sphinx` and `make` with

```bash
apt-get install python3-sphinx make
```

If you don't want to install it globally on your machine, you can run
`python3 simoc.py  --with-dev-backend shell flask-app` and install it in the
`flask-app` container.  Keep in mind that:

1. If the container is destroyed (e.g. by the `down` Docker command) and
   recreated, you will need to reinstall Sphinx and `make`.
2. The `--with-dev-backend` mounts the local dir inside the container.
   This will allow you to access the documentation you built even after
   the container is destroyed.


## Building the documentation

### HTML

To build the HTML documentation:

```bash
cd docs
make html
```

This will build the HTML documentation in the `docs/_build/html` directory.
You can then open the `docs/_build/html/index.html` file with your browser.

### PDF

To build the PDF documentation, you will need to first install some more
dependencies (note that the required latex tools are around 1GB):

```bash
apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended latexmk
```

and then run:

```bash
cd docs
make latexpdf
```

This will create the `docs/_build/latex/SIMOCDevelopersGuide.pdf` file.


## Troubleshooting

If you get the following error:

```bash
# make html
make: *** No rule to make target 'html'.  Stop.
```

you might have forgotten to `cd` in the `docs` directory.  Run `cd docs` and
try again.

If you get other errors, make sure all the dependencies are installed.
