.PHONY: eval test install

PYTHON ?= .venv/bin/python

eval:
	./scripts/run_all.sh

test:
	$(PYTHON) -m pytest

install:
	$(PYTHON) -m pip install -e ".[dev]"
