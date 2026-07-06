# legal-eval-api container image
#
# Build from REPO ROOT (sibling legal-eval/ must be in context):
#   docker build -f legal-eval-api/Dockerfile --ignorefile legal-eval-api/.dockerignore -t legal-eval-api .
#
# legal-eval-api/pyproject.toml uses: legal-eval[agents] @ file:../legal-eval
# pip install MUST run with WORKDIR /app/legal-eval-api and legal-eval at /app/legal-eval.
# Editable installs preserve source paths so config.py and legaleval.paths resolve correctly.

FROM python:3.11-slim-bookworm

# matplotlib / numpy / scikit-learn: prebuilt wheels on bookworm; build-essential as fallback.
# libfreetype + libpng for matplotlib font rendering.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libfreetype6-dev \
        libpng-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY legal-eval /app/legal-eval
COPY legal-eval-api/demo_run/demo /app/legal-eval/results/demo
COPY legal-eval-api /app/legal-eval-api

WORKDIR /app/legal-eval-api

# Install harness editable first (legaleval.paths.project_root() → /app/legal-eval).
# API is installed --no-deps to avoid pip resolving legal-eval twice; runtime deps listed explicitly.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ../legal-eval[agents] \
    && pip install --no-cache-dir \
        "fastapi>=0.115" \
        "uvicorn[standard]>=0.32" \
        "python-multipart>=0.0.9" \
        "cryptography>=42" \
        "httpx>=0.27" \
        "fpdf2>=2.8" \
        "pyyaml>=6" \
        "datasets>=3.0" \
        "pypdf>=5.0" \
        "python-docx>=1.1" \
    && pip install --no-cache-dir --no-deps -e .

# SQLite DB, datasets, run job metadata (see storage.py / db.py).
# Mount a volume at /data in prod; ephemeral inside the container by default.
ENV LEGAL_EVAL_API_DATA=/data

# Fernet master key for encrypted org secrets (crypto.py).
# In production set via Google Secret Manager — do NOT bake into the image.
# If unset, a key file is created under LEGAL_EVAL_API_DATA/.master_key (lost on ephemeral disk).
# ENV LEGAL_EVAL_MASTER_KEY=

# Harness writes run artifacts under /app/legal-eval/results/ (legaleval.paths.project_root).
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV PYTHONUNBUFFERED=1
ENV LEGAL_EVAL_API_HOST=0.0.0.0

# Cloud Run injects PORT at runtime (default 8080 locally).
ENV PORT=8080

RUN mkdir -p /data /tmp/matplotlib /app/legal-eval/results

EXPOSE 8080

# Bind 0.0.0.0 and honor Cloud Run PORT (not hardcoded 8787 from local dev).
CMD ["sh", "-c", "exec uvicorn legal_eval_api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
