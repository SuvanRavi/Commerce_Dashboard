import os
import random
from datetime import datetime, timedelta, timezone

import pandas as pd
from faker import Faker
from google.cloud import bigquery
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET    = os.getenv("BQ_DATASET", "ecommerce_raw")

fake = Faker()
client = bigquery.Client(project=PROJECT_ID)
INGESTED_AT = datetime.now(timezone.utc).isoformat()

# DATA GENERATION CONFIGS

NUM_USERS = 50
NUM_CARTS = 500
MAX_ITEMS = 4
PRODUCT_IDS = list(range(1,21)) # DONT CHANGE. NUMBER BASED ON FakeStore API
CATEGORIES = ['electronics', 'jewelery', "men's clothing", "women's clothing"]  

# Generate users

def generate_users(n:int) -> pd.DataFrame:
    rows = []
    for i in range(1, n+1):
        rows.append({
            "id": i + 200,
            "email": fake.email(),
            "username": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": fake.phone_number(),
            "city": fake.city(),
            "zipcode": fake.zipcode(),
            "ingested_at": INGESTED_AT,
        })
    return pd.DataFrame(rows)

# Generate carts

def generate_carts(n: int, user_ids: list, product_ids: list) -> pd.DataFrame:
    rows = []
    cart_id = random.randint(200, 1000)   # offset to avoid collision with real API carts

    # Generate dates spread across the last 2 years for meaningful time series
    start_date = datetime.now() - timedelta(days=730)

    for _ in range(n):
        user_id    = random.choice(user_ids)
        order_date = start_date + timedelta(days=random.randint(0, 730))
        num_items  = random.randint(1, MAX_ITEMS)

        # Each cart can have multiple products (line items)
        chosen_products = random.sample(product_ids, min(num_items, len(product_ids)))

        for product_id in chosen_products:
            rows.append({
                "cart_id":    cart_id,
                "user_id":    user_id,
                "cart_date":  order_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "product_id": product_id,
                "quantity":   random.randint(1, 4),
                "ingested_at": INGESTED_AT,
            })

        cart_id += 1

    return pd.DataFrame(rows)

# Loading to BigQuery

def load(df: pd.DataFrame, table: str):
    table_id = f"{PROJECT_ID}.{DATASET}.{table}"
    job_config = bigquery.LoadJobConfig(
        write_disposition= bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=True,
    )
    print(f"Loading {len(df)} rows into {table_id}")
    job = client.load_table_from_dataframe(df, table_id, job_config= job_config)
    job.result()
    print(f"Loaded {job.output_rows} rows into {table_id}")

# Main execution
if __name__ == "__main__":
    print("Generating synthetic users...")
    df_users = generate_users(NUM_USERS)
    load(df_users, "users")

    # Carts — use combined real + synthetic user IDs
    all_user_ids = list(range(1, 9)) + list(df_users["id"])  # 8 real + 200 synthetic
    df_carts = generate_carts(NUM_CARTS, all_user_ids, PRODUCT_IDS)
    load(df_carts, "carts")

    print("\nSeeding complete.")
    print(f"  Users added : {NUM_USERS}")
    print(f"  Carts added : {NUM_CARTS}")