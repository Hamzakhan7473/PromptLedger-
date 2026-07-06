.PHONY: install eval smoke sync-ui product test ui-dev ui-build api dev setup-local

# Delegate to legal-eval; pass args via ARGS=, e.g. make eval ARGS='--models openai,google'
ARGS ?=

setup-local:
	@test -f legal-eval/.env || cp legal-eval/.env.example legal-eval/.env
	@test -f legal-eval/models.yaml || cp legal-eval/models.yaml.example legal-eval/models.yaml
	@echo "Edit legal-eval/.env with your API keys, then: make api && make ui-dev"

install:
	$(MAKE) -C legal-eval install
	cd legal-eval-ui && npm install
	cd legal-eval-api && ../legal-eval/.venv/bin/pip install -q -e ../legal-eval[agents] -e . 2>/dev/null || pip install -q -e ../legal-eval[agents] -e .

eval:
	$(MAKE) -C legal-eval eval ARGS="$(ARGS)"

smoke:
	$(MAKE) -C legal-eval smoke ARGS="$(ARGS)"

sync-ui:
	$(MAKE) -C legal-eval sync-ui ARGS="$(ARGS)"

product:
	./scripts/build-legal-eval-product.sh

test:
	$(MAKE) -C legal-eval test
	cd legal-eval-api && PYTHONPATH=src:../legal-eval/src python -m pytest -q

api:
	./scripts/start-api.sh

ui-dev:
	cd legal-eval-ui && npm run dev

ui-build:
	cd legal-eval-ui && npm run build
