# syntax=docker/dockerfile:1

FROM golang:1.22-alpine AS graphrag-builder
WORKDIR /src
COPY graphrag/ .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/graphrag ./cmd/graphrag

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROMPT_LEDGER_ROOT=/app \
    PORT=8765 \
    GRAPHRAG_BIN=/app/bin/graphrag

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 promptledger \
    && useradd --uid 1000 --gid promptledger --create-home promptledger

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY web/ ./web/
COPY governance/ ./governance/
COPY prompts/ ./prompts/
COPY tests/ ./tests/
COPY packs/ ./packs/
COPY demo/ ./demo/
COPY schemas/ ./schemas/
COPY graphrag/ ./graphrag/

COPY --from=graphrag-builder /out/graphrag /app/bin/graphrag

RUN pip install --no-cache-dir -e ".[web]" \
    && chown -R promptledger:promptledger /app

USER promptledger

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health')"

CMD ["sh", "-c", "uvicorn web.backend.main:app --host 0.0.0.0 --port ${PORT:-8765}"]
