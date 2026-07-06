"""Public demo run seeding."""

from __future__ import annotations

from legal_eval_api.demo_seed import (
    DEMO_RUN_ID,
    DEMO_SHARE_TOKEN,
    public_demo_link,
    seed_public_demo_run,
)


def test_seed_public_demo_run(tmp_path, monkeypatch):
    import legal_eval_api.config as config_mod
    import legal_eval_api.db as db_mod
    import legal_eval_api.demo_seed as demo_mod

    data_root = tmp_path / "data"
    data_root.mkdir()
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "manifest.json").write_text('{"run_id":"demo"}', encoding="utf-8")

    results_root = tmp_path / "results"
    monkeypatch.setattr(config_mod, "DATA_ROOT", data_root)
    monkeypatch.setattr(db_mod, "DATA_ROOT", data_root)
    monkeypatch.setattr(demo_mod, "_BUNDLE_DIR", bundle)
    monkeypatch.setattr(
        demo_mod,
        "run_root",
        lambda run_id: results_root / run_id,
    )

    db_mod.init_db()
    seed_public_demo_run()

    assert (results_root / DEMO_RUN_ID / "manifest.json").exists()
    link = public_demo_link()
    assert link is not None
    assert link["run_id"] == DEMO_RUN_ID
    assert link["token"] == DEMO_SHARE_TOKEN
