#!/bin/bash
# Startup script for the NHS pipeline container.
# The CMD passed to the container decides which mode to run in.

set -euo pipefail

echo "NHS Data Pipeline — starting up"
echo "Environment : ${ENVIRONMENT:-development}"
echo "DuckDB path : ${DUCKDB_PATH:-:memory:}"

# Give any dependent services a moment to be ready
sleep 2

case "${1:-pipeline}" in

  pipeline)
    echo "Running full ELT pipeline..."
    cd /app/nhs_dbt
    dbt deps --quiet
    dbt run --profiles-dir /app/nhs_dbt
    dbt test --profiles-dir /app/nhs_dbt
    echo "Pipeline run complete."
    ;;

  api)
    echo "Starting FastAPI server..."
    exec uvicorn src.api.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      --workers ${API_WORKERS:-2}
    ;;

  worker)
    echo "Starting Prefect worker..."
    exec prefect worker start --pool "nhs-pipeline-pool"
    ;;

  shell)
    echo "Dropping into shell..."
    exec /bin/bash
    ;;

  *)
    echo "Unknown command: $1"
    echo "Valid options: pipeline | api | worker | shell"
    exit 1
    ;;

esac
