"""Shared FastAPI helpers for platform microservices."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_REPO = Path(__file__).resolve().parents[1]
os.environ.setdefault("PROMPT_LEDGER_ROOT", str(_REPO))


def create_service_app(title: str, version: str = "0.1.0") -> FastAPI:
    app = FastAPI(title=title, version=version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": title}

    return app
