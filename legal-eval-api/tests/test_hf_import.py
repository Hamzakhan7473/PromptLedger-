"""Tests for Hugging Face dataset import."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from legal_eval_api.dataset_sources.adapters.identity import identity_adapter
from legal_eval_api.dataset_sources.adapters.legalbench_abercrombie import (
    legalbench_abercrombie_adapter,
)
from legal_eval_api.dataset_sources.huggingface import import_hf_dataset, load_hf_rows
from legal_eval_api.db import init_db
from legal_eval_api.main import app
from legal_eval_api.orgs import register_org
from legal_eval_api.schemas import CreateOrgRequest, HuggingFaceImportRequest


def test_identity_adapter_maps_eval_example_columns() -> None:
    rows = [
        {
            "id": "ex-1",
            "contract_excerpt": "Payment due in 30 days.",
            "category": "Payment Terms",
            "present": True,
            "gold_spans": ["Payment due in 30 days."],
            "contract_title": "MSA",
        },
        {
            "id": "ex-2",
            "contract_excerpt": "No exclusivity.",
            "category": "Exclusivity",
            "present": False,
            "gold_spans": [],
            "contract_title": "MSA",
        },
    ]
    examples = identity_adapter(rows)
    assert len(examples) == 2
    assert examples[0].id == "ex-1"


def test_legalbench_abercrombie_adapter_maps_classification_rows() -> None:
    rows = [
        {"index": "0", "text": "The mark Ivory for elephant tusks.", "answer": "generic"},
        {"index": "1", "text": "The mark Kodak for cameras.", "answer": "arbitrary"},
    ]
    examples = legalbench_abercrombie_adapter(rows)
    assert len(examples) == 2
    assert examples[0].category == "abercrombie_mark_type"
    assert examples[0].gold_spans == ["generic"]
    assert examples[0].present is True


def test_import_hf_dataset_unknown_adapter() -> None:
    with pytest.raises(HTTPException) as exc:
        import_hf_dataset(
            repo_id="nguha/legalbench",
            config="abercrombie",
            split="test",
            max_examples=10,
            adapter_name="not_real",
        )
    assert exc.value.status_code == 400
    assert "Unknown adapter" in exc.value.detail


def test_load_hf_rows_empty_split(monkeypatch) -> None:
    mock_load = MagicMock(return_value=iter([]))
    monkeypatch.setattr(
        "datasets.load_dataset",
        mock_load,
    )

    with pytest.raises(HTTPException) as exc:
        load_hf_rows(
            repo_id="example/repo",
            config="cfg",
            split="test",
            max_examples=5,
        )
    assert exc.value.status_code == 400
    assert "no rows" in exc.value.detail.lower()


def test_import_hf_dataset_success_mocked(monkeypatch) -> None:
    rows = [
        {"index": "0", "text": "The mark Ivory for elephant tusks.", "answer": "generic"},
    ]

    monkeypatch.setattr(
        "legal_eval_api.dataset_sources.huggingface.load_hf_rows",
        lambda **_kwargs: rows,
    )

    examples, adapter = import_hf_dataset(
        repo_id="nguha/legalbench",
        config="abercrombie",
        split="test",
        max_examples=1,
        adapter_name="legalbench_abercrombie",
    )
    assert len(examples) == 1
    assert adapter.warning is not None


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    import legal_eval_api.config as config_mod
    import legal_eval_api.datasets as datasets_mod
    import legal_eval_api.storage as storage_mod

    data_root = tmp_path / "data"
    datasets_dir = data_root / "datasets"
    monkeypatch.setattr(config_mod, "DATA_ROOT", data_root)
    monkeypatch.setattr(config_mod, "DATASETS_DIR", datasets_dir)
    monkeypatch.setattr(config_mod, "RUNS_META_DIR", data_root / "runs")
    monkeypatch.setattr(config_mod, "JOB_CONFIGS_DIR", data_root / "job_configs")
    monkeypatch.setattr(storage_mod, "DATASETS_DIR", datasets_dir)
    monkeypatch.setattr(datasets_mod, "DATASETS_DIR", datasets_dir)

    init_db()
    org = register_org(CreateOrgRequest(name="HF Import Co"))
    client = TestClient(app)
    return client, org.api_key


def test_api_list_adapters() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/datasets/adapters")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert "identity" in names
    assert "legalbench_abercrombie" in names


def test_api_import_huggingface_success(api_client, monkeypatch) -> None:
    client, api_key = api_client
    rows = [
        {"index": "0", "text": "The mark Ivory for elephant tusks.", "answer": "generic"},
        {"index": "1", "text": "The mark Kodak for cameras.", "answer": "arbitrary"},
    ]

    monkeypatch.setattr(
        "legal_eval_api.dataset_sources.huggingface.load_hf_rows",
        lambda **_kwargs: rows,
    )

    response = client.post(
        "/api/v1/datasets/import/huggingface",
        json={
            "repo_id": "nguha/legalbench",
            "config": "abercrombie",
            "split": "test",
            "max_examples": 2,
            "adapter": "legalbench_abercrombie",
            "name": "LegalBench abercrombie (test)",
        },
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["example_count"] == 2
    assert body["warning"]
    assert "classification" in body["warning"].lower()


def test_api_import_huggingface_unknown_adapter(api_client) -> None:
    client, api_key = api_client
    response = client.post(
        "/api/v1/datasets/import/huggingface",
        json={
            "repo_id": "nguha/legalbench",
            "config": "abercrombie",
            "split": "test",
            "max_examples": 5,
            "adapter": "missing_adapter",
        },
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 400


def test_ingest_hf_dataset_rejects_judge_pool(api_client, monkeypatch) -> None:
    client, api_key = api_client
    rows = [
        {
            "id": "only-absent",
            "contract_excerpt": "No clause.",
            "category": "X",
            "present": False,
            "gold_spans": [],
            "contract_title": "T",
        },
    ]
    monkeypatch.setattr(
        "legal_eval_api.dataset_sources.huggingface.load_hf_rows",
        lambda **_kwargs: rows,
    )

    response = client.post(
        "/api/v1/datasets/import/huggingface",
        json={
            "repo_id": "custom/eval",
            "config": None,
            "split": "test",
            "max_examples": 5,
            "adapter": "identity",
        },
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 400
    assert "judge validation" in response.json()["detail"].lower()
