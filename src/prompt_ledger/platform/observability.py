from __future__ import annotations

from typing import Any

from prompt_ledger.platform.config import load_platform_yaml


def observability_stack() -> dict[str, Any]:
    """Describe Langfuse, Prometheus, Grafana, OpenTelemetry wiring (config-only in OSS)."""
    raw = load_platform_yaml("observability.yaml")
    return {
        "tracing": raw.get("tracing", {}),
        "metrics": raw.get("metrics", {}),
        "llm_observability": raw.get("llm_observability", {}),
        "storage": raw.get("storage", {}),
        "status": "configured",
        "note": "Export OTEL/Langfuse from orchestrator when keys are set",
    }
