#!/usr/bin/env bash
# CLI demo: run all vertical pipelines and print pass/fail summary.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PROMPT_LEDGER_ROOT="$ROOT"
exec "$ROOT/.venv/bin/python" - <<'PY'
import json
from prompt_ledger.demo import run_vertical_demo

print("PromptLedger — all verticals\n")
all_ok = True
for vid in ("legal", "fintech", "healthcare", "general"):
    r = run_vertical_demo(vid)
    ok = (
        r["audit"]["passed"]
        and r["scenarios"]["passed"]
        and r["manifest"]["passed"]
        and r["pack"]["passed"]
    )
    all_ok = all_ok and ok
    icon = "PASS" if ok else "FAIL"
    print(f"  [{icon}] {vid:12} prompt={r['config']['prompt_id']}")
print()
if not all_ok:
    raise SystemExit(1)
print("All verticals passed.")
PY
