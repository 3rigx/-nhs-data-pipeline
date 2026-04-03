FROM python:3.14-slim AS base

LABEL org.opencontainers.image.title="NHS Data Pipeline"
LABEL org.opencontainers.image.description="End-to-end NHS ELT pipeline: dbt, DuckDB, OMOP CDM, Clinical NLP"
LABEL org.opencontainers.image.source="https://github.com/3rigx/-nhs-data-pipeline"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

FROM base AS builder

RUN poetry install --no-root --only main

RUN poetry run python -m spacy download en_core_web_sm

FROM base AS final

RUN groupadd --gid 1001 pipeline && \
    useradd --uid 1001 --gid pipeline --shell /bin/bash --create-home pipeline

COPY --from=builder /app/.venv /app/.venv
COPY --chown=pipeline:pipeline . .

ENV PATH="/app/.venv/bin:$PATH" \
    DBT_PROFILES_DIR=/app/nhs_dbt \
    DUCKDB_PATH=/data/nhs_pipeline.duckdb

RUN mkdir -p /data && chown pipeline:pipeline /data

USER pipeline

ENTRYPOINT ["python", "-m", "src.pipeline.main"]
CMD []
