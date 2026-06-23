"""Load CUAD v1 and build a balanced legal clause-presence eval set."""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

CUAD_URL = (
    "https://huggingface.co/datasets/theatticusproject/cuad/"
    "resolve/main/CUAD_v1/CUAD_v1.json"
)
CATEGORY_PATTERN = re.compile(r'related to "([^"]+)"')

DEFAULT_N_CATEGORIES = 6
DEFAULT_N_PER_CATEGORY = 25
DEFAULT_MAX_CHARS = 8000
DEFAULT_SEED = 42


class EvalExample(BaseModel):
    id: str
    contract_excerpt: str
    category: str
    present: bool
    gold_spans: list[str]
    contract_title: str


@dataclass(frozen=True)
class NormalizedQA:
    category: str
    present: bool
    gold_spans: list[str]
    answer_starts: list[int]


@dataclass(frozen=True)
class NormalizedContract:
    title: str
    context: str
    qas: tuple[NormalizedQA, ...]


def project_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"


def extract_category(question: str) -> str | None:
    match = CATEGORY_PATTERN.search(question)
    return match.group(1) if match else None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def download_cuad(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", CUAD_URL, follow_redirects=True, timeout=120.0) as response:
        response.raise_for_status()
        with dest.open("wb") as handle:
            for chunk in response.iter_bytes():
                handle.write(chunk)
    return dest


def load_cuad_json(path: Path | None = None, *, download: bool = True) -> dict:
    data_path = path or (project_data_dir() / "CUAD_v1.json")
    if not data_path.exists():
        if download:
            download_cuad(data_path)
        else:
            raise FileNotFoundError(f"CUAD dataset not found at {data_path}")
    with data_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_cuad(raw: dict) -> list[NormalizedContract]:
    contracts: list[NormalizedContract] = []
    for article in raw["data"]:
        title = article["title"]
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            qas: list[NormalizedQA] = []
            for qa in paragraph["qas"]:
                category = extract_category(qa["question"])
                if category is None:
                    continue
                answers = qa.get("answers") or []
                impossible = bool(qa.get("is_impossible", False))
                if impossible or not answers:
                    normalized = NormalizedQA(
                        category=category,
                        present=False,
                        gold_spans=[],
                        answer_starts=[],
                    )
                else:
                    normalized = NormalizedQA(
                        category=category,
                        present=True,
                        gold_spans=[answer["text"] for answer in answers],
                        answer_starts=[answer["answer_start"] for answer in answers],
                    )
                qas.append(normalized)
            contracts.append(
                NormalizedContract(title=title, context=context, qas=tuple(qas))
            )
    return contracts


def cap_excerpt(
    context: str,
    gold_spans: list[str],
    answer_starts: list[int],
    max_chars: int,
) -> str:
    if len(context) <= max_chars:
        return context

    if not gold_spans or not answer_starts:
        return context[:max_chars]

    span_bounds = [
        (start, start + len(span))
        for start, span in zip(answer_starts, gold_spans, strict=True)
    ]
    min_start = min(start for start, _ in span_bounds)
    max_end = max(end for _, end in span_bounds)
    span_width = max_end - min_start

    if span_width >= max_chars:
        return context[min_start:max_end]

    extra = max_chars - span_width
    window_start = max(0, min_start - extra // 2)
    window_end = window_start + max_chars
    if window_end > len(context):
        window_end = len(context)
        window_start = max(0, window_end - max_chars)
    return context[window_start:window_end]


def _example_sort_key(
    contract: NormalizedContract, qa: NormalizedQA
) -> tuple[str, str, bool]:
    return (qa.category, contract.title, qa.present)


def _pools_by_category(
    contracts: list[NormalizedContract],
) -> tuple[dict[str, list[tuple[NormalizedContract, NormalizedQA]]], dict[str, list[tuple[NormalizedContract, NormalizedQA]]]]:
    present_pool: dict[str, list[tuple[NormalizedContract, NormalizedQA]]] = {}
    absent_pool: dict[str, list[tuple[NormalizedContract, NormalizedQA]]] = {}

    for contract in contracts:
        for qa in contract.qas:
            pool = present_pool if qa.present else absent_pool
            pool.setdefault(qa.category, []).append((contract, qa))

    for pool in (present_pool, absent_pool):
        for category in pool:
            pool[category].sort(key=lambda item: _example_sort_key(item[0], item[1]))

    return present_pool, absent_pool


def select_categories(
    present_pool: dict[str, list[tuple[NormalizedContract, NormalizedQA]]],
    absent_pool: dict[str, list[tuple[NormalizedContract, NormalizedQA]]],
    *,
    categories: list[str] | None,
    n_categories: int,
    n_per_category: int,
) -> list[str]:
    if categories is not None:
        return categories

    min_each = (n_per_category + 1) // 2
    eligible = [
        category
        for category in sorted(present_pool)
        if category in absent_pool
        and len(present_pool[category]) >= min_each
        and len(absent_pool[category]) >= min_each
    ]
    if len(eligible) < n_categories:
        raise ValueError(
            f"Need {n_categories} categories with at least {min_each} present and "
            f"absent examples; found {len(eligible)}"
        )
    return eligible[:n_categories]


def _sample_eval_examples(
    contracts: list[NormalizedContract],
    *,
    categories: list[str] | None,
    n_categories: int,
    n_per_category: int,
    max_chars: int,
    seed: int,
) -> list[EvalExample]:
    present_pool, absent_pool = _pools_by_category(contracts)
    selected = select_categories(
        present_pool,
        absent_pool,
        categories=categories,
        n_categories=n_categories,
        n_per_category=n_per_category,
    )

    n_present = n_per_category // 2
    n_absent = n_per_category - n_present
    rng = random.Random(seed)

    examples: list[EvalExample] = []
    example_index = 0

    for category in selected:
        present_items = present_pool[category]
        absent_items = absent_pool[category]
        if len(present_items) < n_present or len(absent_items) < n_absent:
            raise ValueError(
                f"Category {category!r} has insufficient examples: "
                f"need {n_present} present and {n_absent} absent, "
                f"have {len(present_items)} present and {len(absent_items)} absent"
            )
        present_samples = rng.sample(present_items, n_present)
        absent_samples = rng.sample(absent_items, n_absent)
        for contract, qa in present_samples + absent_samples:
            excerpt = cap_excerpt(
                contract.context,
                qa.gold_spans,
                qa.answer_starts,
                max_chars,
            )
            examples.append(
                EvalExample(
                    id=f"cuad-{example_index:05d}",
                    contract_excerpt=excerpt,
                    category=qa.category,
                    present=qa.present,
                    gold_spans=list(qa.gold_spans),
                    contract_title=contract.title,
                )
            )
            example_index += 1

    examples.sort(key=lambda item: item.id)
    return examples


def build_eval_set(
    cuad_path: Path | None = None,
    *,
    categories: list[str] | None = None,
    n_categories: int = DEFAULT_N_CATEGORIES,
    n_per_category: int = DEFAULT_N_PER_CATEGORY,
    max_chars: int = DEFAULT_MAX_CHARS,
    seed: int = DEFAULT_SEED,
    download: bool = True,
) -> list[EvalExample]:
    raw = load_cuad_json(cuad_path, download=download)
    contracts = normalize_cuad(raw)
    return _sample_eval_examples(
        contracts,
        categories=categories,
        n_categories=n_categories,
        n_per_category=n_per_category,
        max_chars=max_chars,
        seed=seed,
    )


def write_eval_set_jsonl(
    examples: list[EvalExample],
    output_path: Path | None = None,
) -> Path:
    path = output_path or (project_data_dir() / "eval_set.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(example.model_dump_json() + "\n")
    return path


def read_eval_set_jsonl(path: Path) -> list[EvalExample]:
    examples: list[EvalExample] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                examples.append(EvalExample.model_validate_json(line))
    return examples


def build_eval_set_from_raw(
    raw: dict,
    *,
    categories: list[str] | None = None,
    n_categories: int = DEFAULT_N_CATEGORIES,
    n_per_category: int = DEFAULT_N_PER_CATEGORY,
    max_chars: int = DEFAULT_MAX_CHARS,
    seed: int = DEFAULT_SEED,
) -> list[EvalExample]:
    """Build an eval set from an in-memory CUAD JSON object (for tests)."""
    contracts = normalize_cuad(raw)
    return _sample_eval_examples(
        contracts,
        categories=categories,
        n_categories=n_categories,
        n_per_category=n_per_category,
        max_chars=max_chars,
        seed=seed,
    )


def main() -> None:
    examples = build_eval_set()
    output_path = write_eval_set_jsonl(examples)
    print(f"Wrote {len(examples)} examples to {output_path}")


if __name__ == "__main__":
    main()
