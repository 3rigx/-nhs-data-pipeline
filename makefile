# ============================================
# NHS Data Pipeline - Makefile
# ============================================
.PHONY: help setup generate-data dbt-run dbt-test nlp api test lint clean

help: ## Show this help message
	@echo "NHS Data Pipeline - Available Commands"
	@echo "======================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*
$$
' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n",
$$
1, $\$2}'

setup: ## Initial project setup
	poetry install
	poetry run pre-commit install
	cp -n .env.example .env || true
	@echo "Setup complete!"

generate-data: ## Generate synthetic NHS data
	poetry run python src/ingestion/generate_synthetic_data.py

dbt-run: ## Run all dbt models
	cd nhs_dbt && poetry run dbt run

dbt-test: ## Run dbt tests
	cd nhs_dbt && poetry run dbt test

dbt-docs: ## Generate and serve dbt documentation
	cd nhs_dbt && poetry run dbt docs generate && poetry run dbt docs serve

nlp: ## Run NLP pipeline on clinical notes
	poetry run python src/nlp/run_pipeline.py

api: ## Start the FastAPI server
	poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	poetry run pytest tests/ -v --cov=src

lint: ## Run all linters
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/

format: ## Format all code
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