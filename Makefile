.PHONY: install eval smoke sync-ui product test ui-dev ui-build

# Delegate to legal-eval; pass args via ARGS=, e.g. make eval ARGS='--models openai,google'
ARGS ?=

install:
	$(MAKE) -C legal-eval install
	cd legal-eval-ui && npm install

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

ui-dev:
	cd legal-eval-ui && npm run dev

ui-build:
	cd legal-eval-ui && npm run build
