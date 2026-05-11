FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dbt-bigquery

COPY ingestion/synthetic_data.py .

COPY ecommerce_dbt/ ecommerce_dbt/

# Copy dbt profiles into the location dbt expects
COPY ecommerce_dbt/profiles/profiles.yml /root/.dbt/profiles.yml

COPY ingestion/run_pipeline.sh .
RUN chmod +x run_pipeline.sh

CMD ["./run_pipeline.sh"]