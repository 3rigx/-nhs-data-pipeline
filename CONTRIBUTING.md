# Contributing to NHS Data Pipeline

## Getting Started

```bash
git clone https://github.com/3rigx/-nhs-data-pipeline.git
cd -nhs-data-pipeline
poetry install
poetry run pre-commit install
```

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Protected. Only merge via PR after CI passes. |
| `develop` | Integration branch for feature work. |
| `feat/*` | New features (`feat/add-omop-drug-era`) |
| `fix/*` | Bug fixes (`fix/dbt-null-nhs-number`) |
| `chore/*` | Maintenance, deps, config |
| `docs/*` | Documentation only |

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(optional scope): <description>

feat(dbt): add drug era intermediate model
fix(api): handle missing patient_id in FHIR endpoint
docs(readme): update architecture diagram
chore(deps): bump dbt-core to 1.8.0
ci: add bandit security scan to PR checks
test(nlp): add spaCy entity extraction unit tests
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`

## Running Tests Locally

```bash
# All tests
poetry run pytest tests/ -v

# With coverage
poetry run pytest tests/ --cov=src --cov-report=term-missing

# Specific module
poetry run pytest tests/test_api.py -v
```

## dbt Development

```bash
# Compile models
cd nhs_dbt && poetry run dbt compile

# Run staging only
poetry run dbt run --select staging

# Run all tests
poetry run dbt test

# Generate docs
poetry run dbt docs generate && poetry run dbt docs serve
```

## Linting Locally

```bash
# Python linting
poetry run ruff check src/ tests/
poetry run black --check src/ tests/

# Auto-fix
poetry run ruff check --fix src/ tests/
poetry run black src/ tests/

# SQL linting
poetry run sqlfluff lint nhs_dbt/models/ --dialect duckdb
```

## Security

- Never commit secrets, API keys, or patient-identifiable data
- All patient data in this repo is **fully synthetic**
- Run `bandit -r src/` before submitting any PR
- Check `.env.example` — never commit a populated `.env`

## Pull Request Process

1. Branch from `develop` (or `main` for hotfixes)
2. Follow the PR template
3. Ensure all CI checks pass (green ✅)
4. Request review from at least one maintainer
5. Squash-merge into `main`