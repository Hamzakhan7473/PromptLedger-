"""Org usage statistics for enterprise dashboard."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from legal_eval_api.schemas import OrgStats
from legal_eval_api.storage import read_json, run_meta_path


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_org_stats(org_id: str) -> OrgStats:
    now = datetime.now(UTC)
    week_ago = now - timedelta(days=7)

    total = completed = failed = running = queued = 0
    agent_runs = eval_runs = 0
    durations: list[float] = []

    for path in sorted(run_meta_path("").parent.glob("*.json")):
        meta = read_json(path)
        if meta.get("org_id") != org_id:
            continue
        total += 1
        status = meta.get("status")
        if status == "completed":
            completed += 1
        elif status == "failed":
            failed += 1
        elif status == "running":
            running += 1
        elif status == "queued":
            queued += 1

        if meta.get("mode") == "agent":
            agent_runs += 1
        else:
            eval_runs += 1

        started = _parse_dt(meta.get("started_at"))
        finished = _parse_dt(meta.get("finished_at"))
        if started and finished and finished >= started:
            durations.append((finished - started).total_seconds())

        created = _parse_dt(meta.get("created_at"))
        if created and created >= week_ago:
            pass  # counted below via recent list

    recent = 0
    for path in run_meta_path("").parent.glob("*.json"):
        meta = read_json(path)
        if meta.get("org_id") != org_id:
            continue
        created = _parse_dt(meta.get("created_at"))
        if created and created >= week_ago:
            recent += 1

    finished_count = completed + failed
    success_rate = (completed / finished_count) if finished_count else None
    avg_duration = (sum(durations) / len(durations)) if durations else None

    return OrgStats(
        org_id=org_id,
        total_runs=total,
        completed_runs=completed,
        failed_runs=failed,
        running_runs=running,
        queued_runs=queued,
        eval_runs=eval_runs,
        agent_runs=agent_runs,
        runs_last_7_days=recent,
        success_rate=round(success_rate, 4) if success_rate is not None else None,
        avg_duration_seconds=round(avg_duration, 1) if avg_duration is not None else None,
    )
