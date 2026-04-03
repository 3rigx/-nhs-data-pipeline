# ============================================
# NHS Data Pipeline - Makefile
# ============================================
.PHONY: help setup generate-data dbt-run dbt-test dbt-docs nlp api test lint format clean \
        docker-up docker-down docker-build docker-clean docker-logs docker-shell \
        docker-test docker-dbt-run docker-dbt-test deploy


help: ## Show this help message
	@echo "NHS Data Pipeline - Available Commands"
	@echo "======================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'


# ── Local development (Poetry) ───────────────────────────────────────────────

setup: ## Initial project setup
	poetry install
	poetry run pre-commit install
	cp -n .env.example .env || true
	@echo "Setup complete!"

generate-data: ## Generate synthetic NHS data
	poetry run python src/ingestion/generate_synthetic_data.py

dbt-run: ## Run all dbt models (local)
	cd nhs_dbt && poetry run dbt run

dbt-test: ## Run dbt tests (local)
	cd nhs_dbt && poetry run dbt test

dbt-docs: ## Generate and serve dbt documentation (local)
	cd nhs_dbt && poetry run dbt docs generate && poetry run dbt docs serve

nlp: ## Run NLP pipeline on clinical notes (local)
	poetry run python src/nlp/run_pipeline.py

api: ## Start the FastAPI server (local, hot-reload)
	poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests (local)
	poetry run pytest tests/ -v --cov=src

lint: ## Run all linters (local)
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/

format: ## Format all code (local)
	poetry run ruff check --fix src/ tests/
	poetry run black src/ tests/

clean: ## Clean generated files
	rm -rf nhs_dbt/target/
	rm -rf nhs_dbt/dbt_packages/
	rm -rf nhs_dbt/logs/
	rm -rf data/duckdb/*.duckdb
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov/
	@echo "Cleaned!"


# ── Docker stack ─────────────────────────────────────────────────────────────

docker-up: ## Start the full Docker stack (API, Prefect, dbt-docs)
	docker compose up --build -d
	@echo ""
	@echo "  API        → http://localhost:8000"
	@echo "  API docs   → http://localhost:8000/docs"
	@echo "  Prefect UI → http://localhost:4200"
	@echo "  dbt docs   → http://localhost:8081"

docker-down: ## Stop the Docker stack (keeps volumes)
	docker compose down

docker-build: ## Build Docker images without starting
	docker compose build

docker-clean: ## Stop Docker stack and wipe all data volumes
	docker compose down -v
	@echo "All volumes removed."

docker-logs: ## Follow logs for all Docker services
	docker compose logs -f

docker-shell: ## Open a shell inside the pipeline container
	docker compose exec pipeline /bin/bash

docker-test: ## Run pytest inside Docker
	docker compose run --rm pipeline pytest tests/ -v

docker-dbt-run: ## Run dbt inside Docker
	docker compose exec pipeline bash -c "cd nhs_dbt && dbt run"

docker-dbt-test: ## Run dbt tests inside Docker
	docker compose exec pipeline bash -c "cd nhs_dbt && dbt test"

deploy: ## Production deploy using GHCR images
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
