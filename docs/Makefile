# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
PYTHON        = python3
VENVDIR       = ./venv
BUILDDIR      = _build
SPHINXOPTS    =
SPHINXBUILD   = $(VENVDIR)/bin/sphinx-build
SPHINXLINT    = $(VENVDIR)/bin/sphinx-lint
SPHINXPROJ    = SIMOCDevelopersGuide
SOURCEDIR     = .
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


clean: clean-venv
	-rm -rf $(BUILDDIR)/*

clean-venv:
	rm -rf $(VENVDIR)

venv:
	@if [ -d $(VENVDIR) ] ; then \
		echo "venv already exists."; \
		echo "To recreate it, remove it first with \`make clean-venv'."; \
	else \
		$(MAKE) ensure-venv; \
	fi

ensure-venv:
	@if [ ! -d $(VENVDIR) ] ; then \
		$(PYTHON) -m venv $(VENVDIR); \
		$(VENVDIR)/bin/python3 -m pip install --upgrade pip; \
		$(VENVDIR)/bin/python3 -m pip install -r requirements.txt; \
		echo "The venv has been created in the $(VENVDIR) directory"; \
	fi

html: ensure-venv
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

pdf: ensure-venv
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	make -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

check: ensure-venv
	# Ignore the tools and venv dirs and check that the default role is not used.
	$(SPHINXLINT) -i $(VENVDIR) --enable default-role

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
