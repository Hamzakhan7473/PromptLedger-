from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml


@dataclass(frozen=True)
class PromptVersion:
    version: str
    system: str
    user: str
    variables: list[str]
    output_schema: str | None
    audit_overrides: dict[str, Any]


@dataclass(frozen=True)
class PromptPack:
    prompt_id: str
    domain: str
    description: str
    metadata: dict[str, Any]
    versions: dict[str, PromptVersion]


def load_prompt_pack(path: Path) -> PromptPack:
    raw = read_yaml(path)
    pid = raw["id"]
    domain = raw.get("domain", "unknown")
    description = raw.get("description", "")
    metadata = raw.get("metadata", {})
    versions_raw: dict[str, Any] = raw["versions"]
    versions: dict[str, PromptVersion] = {}
    for ver, body in versions_raw.items():
        versions[ver] = PromptVersion(
            version=ver,
            system=str(body["system"]),
            user=str(body["user"]),
            variables=list(body.get("variables", [])),
            output_schema=body.get("output_schema"),
            audit_overrides=dict(body.get("audit_overrides", {})),
        )
    return PromptPack(
        prompt_id=pid,
        domain=domain,
        description=description,
        metadata=metadata,
        versions=versions,
    )


def discover_registry(registry_root: Path) -> dict[str, PromptPack]:
    packs: dict[str, PromptPack] = {}
    for path in sorted(registry_root.rglob("*.yaml")):
        pack = load_prompt_pack(path)
        if pack.prompt_id in packs:
            raise ValueError(f"Duplicate prompt id {pack.prompt_id}: {path}")
        packs[pack.prompt_id] = pack
    return packs


def get_version(pack: PromptPack, version: str) -> PromptVersion:
    if version not in pack.versions:
        raise KeyError(f"Unknown version {version} for {pack.prompt_id}")
    return pack.versions[version]
