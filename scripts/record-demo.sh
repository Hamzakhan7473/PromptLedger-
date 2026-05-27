#!/usr/bin/env bash
# Start the demo UI after pre-flight checks (for screen recording).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

"$ROOT/scripts/demo-check.sh"

echo ""
echo "=============================================="
echo "  Recording: open http://127.0.0.1:${PORT:-8765}"
echo "  Follow timestamps in DEMO_RECORD.md"
echo "  API docs: http://127.0.0.1:${PORT:-8765}/docs"
echo "=============================================="
echo ""

exec "$ROOT/scripts/run-web.sh"
