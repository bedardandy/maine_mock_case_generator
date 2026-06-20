.PHONY: help install list generate fill compound probate smoke test examples clean

help:
	@echo "Mock Legal Matter Generator"
	@echo ""
	@echo "  make install    Install Python dependencies"
	@echo "  make list       List available scenarios"
	@echo "  make generate   Generate one matter (SCENARIO=<id> SEED=<n>)"
	@echo "  make fill       Fill a downstream form (FORM=<id>)"
	@echo "  make compound   Summarize a compound universe (COMPOUND=<id>)"
	@echo "  make smoke      Run the end-to-end smoke test (scenarios, fills, compounds)"
	@echo "  make examples   Regenerate the committed examples/"
	@echo "  make test       Run the pytest suite"
	@echo "  make clean      Remove generated output and caches"

install:
	pip install -r requirements.txt

list:
	python3 tools/generate.py --list

# Usage: make generate SCENARIO=family-divorce-cumberland SEED=1
SCENARIO ?= family-divorce-cumberland
SEED ?= 1
generate:
	python3 tools/generate.py $(SCENARIO) --seed $(SEED)

smoke:
	python3 tools/smoke.py --count 5

# Usage: make fill FORM=FM-004
FORM ?= FM-004
fill:
	python3 tools/fill.py $(FORM) --seed 1

# Usage: make compound COMPOUND=death-cascade
COMPOUND ?= death-cascade
compound:
	python3 tools/compound.py $(COMPOUND) --seed 1 --summary

# Usage: make probate PFORM=DE-401
PFORM ?= DE-401
probate:
	python3 tools/probate_case.py $(PFORM) --seed 7

examples:
	python3 tools/build_examples.py

test:
	python3 -m pytest -q

clean:
	rm -rf out
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
