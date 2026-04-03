# Development Guide

Everything you need to get the project running locally, understand the codebase,
and contribute changes confidently.

---

## Prerequisites

Before you start, make sure you have the following installed:

| Tool | Minimum version | Install guide |
|---|---|---|
| Python | 3.11 | https://python.org |
| Poetry | 1.8 | https://python-poetry.org/docs/ |
| Docker Desktop | 4.x | https://docs.docker.com/desktop/ |
| Git | 2.x | https://git-scm.com |

---

## First-time setup

```bash
# Clone the repository
git clone https://github.com/3rigx/-nhs-data-pipeline.git
cd -nhs-data-pipeline

# Install all dependencies (including dev tools)
poetry install

# Install pre-commit hooks — these run ruff and black before every commit
poetry run pre-commit install

# Copy the environment file and fill in any values you need
cp .env.example .env
```

That is everything. You should now be able to run any command in this guide.

---

## Environment variables

The `.env` file controls how the pipeline behaves. The key variables are:

| Variable | Default | Description |
|---|---|---|
| `DUCKDB_PATH` | `data/duckdb/nhs_pipeline.duckdb` | Path to the DuckDB database file |
| `ENVIRONMENT` | `development` | Controls logging level and API behaviour |
| `NLP_BACKEND` | `spacy` | Set to `medcat` to use MedCAT instead |
| `API_WORKERS` | `2` | Number of Uvicorn worker processes |
| `PREFECT_API_URL` | `http://localhost:4200/api` | Prefect server URL |

Never commit a populated `.env` file. The `.gitignore` already excludes it.

---

## Generating synthetic data

The data generator creates realistic but entirely fictional NHS patient records.
Nothing it produces represents a real person.

```bash
poetry run python src/ingestion/generate_synthetic_data.py
```

This writes CSV and Parquet files to `data/raw/` and loads them into DuckDB.
Default output is 1,000 patients with associated episodes, prescriptions, and clinical notes.
To change the volume, edit the `PATIENT_COUNT` constant in the generator.

---

## Running dbt

All dbt commands should be run from inside the `nhs_dbt/` directory:

```bash
cd nhs_dbt

# Install dbt packages (run once after cloning)
poetry run dbt deps

# Compile all models (checks SQL is valid without running)
poetry run dbt compile

# Run all models
poetry run dbt run

# Run only the staging layer
poetry run dbt run --select staging

# Run data quality tests
poetry run dbt test

# Generate and serve the model lineage docs
poetry run dbt docs generate
poetry run dbt docs serve
```

---

## Running the API

```bash
# Start with hot-reload for development
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API docs will be at http://localhost:8000/docs.

---

## Running the test suite

```bash
# Full suite with coverage report
poetry run pytest tests/ -v --cov=src

# A specific test file
poetry run pytest tests/test_api.py -v

# Just the dbt-related tests
poetry run pytest tests/test_dbt_models.py -v
```

The CI pipeline requires a minimum coverage of 60%. If you add new code,
add a corresponding test.

---

## Linting and formatting

The project uses ruff for linting and black for formatting.
Pre-commit hooks run these automatically before every commit,
but you can also run them manually:

```bash
# Check for linting issues
poetry run ruff check src/ tests/

# Auto-fix what ruff can fix
poetry run ruff check --fix src/ tests/

# Check formatting
poetry run black --check src/ tests/

# Apply formatting
poetry run black src/ tests/

# Lint SQL models
poetry run sqlfluff lint nhs_dbt/models/ --dialect duckdb
```

---

## Working with Docker

```bash
# Start the full stack
docker compose up --build -d

# Watch the logs
docker compose logs -f

# Run a one-off command inside the pipeline container
docker compose run --rm pipeline python src/ingestion/generate_synthetic_data.py

# Open an interactive shell
docker compose exec pipeline /bin/bash

# Stop everything
docker compose down
```

For the Airflow stack specifically (run from the `docker/` folder):

```bash
cd docker
docker compose -f docker-compose.airflow.yml up -d
```

---

## Branch and commit conventions

Work on a feature branch cut from `main`:

```bash
git checkout -b feat/your-feature-name
```

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(dbt): add drug era intermediate model
fix(api): handle missing patient_id in FHIR endpoint
test(nlp): add negation detection unit tests
chore(deps): bump spacy to 3.8.14
```

Open a pull request against `main` when your work is ready.
The CI pipeline must be green before merging.

---

## Troubleshooting

**`dbt run` fails with "table not found"**
Make sure you have generated data first (`poetry run python src/ingestion/generate_synthetic_data.py`)
and that `DUCKDB_PATH` in your `.env` points to the correct file.

**`poetry install` is slow**
Poetry resolves the full dependency graph from scratch if there is no `poetry.lock` file.
Make sure `poetry.lock` is committed to the repository.

**Docker containers exit immediately**
Run `docker compose logs pipeline` to see the error.
The most common cause is a missing or malformed `.env` file.

**spaCy model not found**
Run `poetry run python -m spacy download en_core_web_sm` to download the model.
This is done automatically in the Docker build but needs to be done manually
in a fresh local environment.
