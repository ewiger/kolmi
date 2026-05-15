# Basic LaTeX build for the paper
TEX=pdflatex
BIBTEX=bibtex
SRC=main
PDF=$(SRC).pdf

.PHONY: all pdf clean veryclean

all: pdf

pdf:
	$(TEX) $(SRC).tex
	$(BIBTEX) $(SRC) || true
	$(TEX) $(SRC).tex
	$(TEX) $(SRC).tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc

veryclean: clean
	rm -f $(PDF)
