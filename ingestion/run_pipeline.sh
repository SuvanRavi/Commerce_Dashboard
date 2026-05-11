#!/bin/bash
set -e

echo "============================================"
echo "Step 1/3 — Running ingestion"
echo "============================================"
python synthetic_data.py

echo "============================================"
echo "Step 2/3 — Running dbt transformations"
echo "============================================"
cd /app/ecommerce_dbt
dbt run --profiles-dir /root/.dbt

echo "============================================"
echo "Step 3/3 — Running dbt tests"
echo "============================================"
dbt test --profiles-dir /root/.dbt

echo "============================================"
echo "Pipeline complete"
echo "============================================"