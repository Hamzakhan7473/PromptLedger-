.PHONY: eval test install smoke sync-ui product

PYTHON ?= .venv/bin/python
# macOS default `make` does not support `make eval -- --flags`.
# Use: make eval ARGS='--models openai,google,bedrock_claude'
ARGS ?=

eval:
	./scripts/run_all.sh $(ARGS)

smoke:
	./scripts/smoke.sh $(ARGS)

sync-ui:
	./scripts/sync-to-ui.sh $(ARGS)

product:
	../scripts/build-legal-eval-product.sh

test:
	$(PYTHON) -m pytest

install:
	$(PYTHON) -m pip install -e ".[dev]"
