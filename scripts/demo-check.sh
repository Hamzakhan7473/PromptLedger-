#!/usr/bin/env bash
# Pre-flight: verify the repo is ready for a live demo or screen recording.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROMPT_LEDGER_ROOT="$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
fail() { echo -e "${RED}FAIL${NC} $*" >&2; exit 1; }
ok() { echo -e "${GREEN}OK${NC} $*"; }

echo "=== PromptLedger demo pre-flight ==="

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -e ".[dev,web]"

ok "Python package installed"
.venv/bin/ruff check src tests >/dev/null || fail "ruff check"
ok "Ruff"

.venv/bin/prompt-ledger audit || fail "audit"
ok "Audit"

.venv/bin/prompt-ledger validate-manifest || fail "validate-manifest"
ok "Manifest"

.venv/bin/prompt-ledger test || fail "scenario tests"
ok "Scenarios (6)"

for pack in packs/*-assistant; do
  .venv/bin/prompt-ledger pack verify "$pack" || fail "pack verify $pack"
  ok "Pack $(basename "$pack")"
done

.venv/bin/pytest -q || fail "pytest"
ok "Pytest"

if command -v go >/dev/null 2>&1; then
  (cd graphrag && go test ./...) || fail "go test"
  ok "GraphRAG Go tests"
else
  echo "WARN: go not installed — skipping GraphRAG tests (bundled indexes still work)"
fi

.venv/bin/python - <<'PY'
import json
from prompt_ledger.demo import run_vertical_demo

for v in ("legal", "fintech", "healthcare", "general"):
    r = run_vertical_demo(v)
    ok = r["audit"]["passed"] and r["scenarios"]["passed"] and r["pack"]["passed"]
    assert ok, f"vertical {v} failed"
    assert r["graphrag"].get("indexed"), f"vertical {v} graphrag"
    print(f"  vertical {v}: pass")
PY
ok "All 4 vertical demos"

.venv/bin/prompt-ledger agent run --env legal --task "Demo clause review" >/dev/null
.venv/bin/prompt-ledger agent evaluate >/dev/null
ok "Agent orchestrator (legal)"

echo ""
echo -e "${GREEN}Ready to record.${NC} Run: ./scripts/record-demo.sh"
echo "Script: DEMO_RECORD.md"
