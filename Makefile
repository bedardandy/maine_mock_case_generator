.PHONY: help install list generate smoke test examples clean

help:
	@echo "Mock Legal Matter Generator"
	@echo ""
	@echo "  make install    Install Python dependencies"
	@echo "  make list       List available scenarios"
	@echo "  make generate   Generate one matter (SCENARIO=<id> SEED=<n>)"
	@echo "  make smoke      Run the end-to-end smoke test across all scenarios"
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

examples:
	python3 tools/build_examples.py

test:
	python3 -m pytest -q

clean:
	rm -rf out
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
