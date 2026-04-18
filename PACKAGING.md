# Packaging and naming

## PyPI / import name

Before publishing to PyPI:

1. **Search** [pypi.org](https://pypi.org) for collisions on your chosen **distribution name** (the string in `pip install …`).
2. The **import package** name (`src/prompt_ledger`) can differ from the distribution name; align naming in `pyproject.toml` `[project]` `name` with whatever you publish.
3. If `promptledger` (or similar) is taken or confusing, prefer a **distinct brand** for the distribution, e.g. `prompt-ledger-governance`, `pl-governance`, or a product-specific name—then document the CLI (`prompt-ledger`) clearly in README.

## GitHub org / repo

- Repo URL and PyPI project should tell the same story; avoid near-duplicate names across orgs.
- If you rebrand, plan a **redirect period** (archive old repo, link from README) to reduce search confusion.

## Go module (`graphrag/`)

- Module path is `promptledger/graphrag` today; for open source, consider a **stable module path** that matches a domain you control (e.g. `github.com/<org>/promptledger/graphrag`) when you are ready to tag releases—avoids churn for downstream imports.

## Versioning

- Tag **Git releases** when the Python CLI or governance contract is stable enough for consumers.
- Keep **changelog** or release notes for manifest/schema breaking changes (`prompts/manifest.yaml`, schema paths).
