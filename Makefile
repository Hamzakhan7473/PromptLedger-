.PHONY: install check demo record verticals test audit k8s-build

install:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e ".[dev,web]"

check:
	./scripts/demo-check.sh

demo:
	./scripts/run-web.sh

record:
	./scripts/record-demo.sh

verticals:
	./scripts/run-all-verticals.sh

test:
	.venv/bin/prompt-ledger test

audit:
	.venv/bin/prompt-ledger audit

k8s-build:
	./scripts/k8s-build.sh

platform:
	./scripts/platform-services.sh

platform-build:
	./scripts/k8s-platform-build.sh
