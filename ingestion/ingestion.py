import os
import logging
from datetime import datetime, timezone
import requests 
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# Configuration

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET = os.getenv("BQ_DATASET", "ecommerce_raw")
BASE_URL = "https://fakestoreapi.com"

TABLES = {
    "products": F"{PROJECT_ID}.{DATASET}.products",
    "carts": F"{PROJECT_ID}.{DATASET}.carts",
    "users": F"{PROJECT_ID}.{DATASET}.users",
}

# Setup logging

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s %(levelname)s %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Helper Functions

# Fetching data from FakeStore API with timeout and logging.
def fetch_endpoint(endpoint:str) -> list[dict]:
    url = f"{BASE_URL}/{endpoint}"
    log.info(f"Fetching {url}")
    response = requests.get(url, timeout = 10)
    response.raise_for_status()
    data = response.json()
    log.info(f" ->{len(data)} records received")
    return data

# Adding metadata of UTC timestamp when pipeline run to each record.
def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df["ingested_at"] = datetime.now(timezone.utc).isoformat()
    return df

# Flattening nested JSON structures for PRODUCTS into tabular form.
def flatten_products(raw: list[dict]) -> pd.DataFrame:
    rows = []
    for item in raw:
        rating = item.pop("rating", {})
        item["rating_rate"] = rating.get("rate")
        item["rating_count"] = rating.get("count")
        rows.append(item)
    df = pd.DataFrame(rows)
    df["id"] = df["id"].astype(int)
    df["price"] = df["price"].astype(float)
    df["rating_rate"] = df["rating_rate"].astype(float)
    df["rating_count"] = df["rating_count"].astype(int)
    return df

# Flattening nested JSON structures for CARTS into tabular form.
def flatten_carts(raw: list[dict]) -> pd.DataFrame:
    rows = []
    for cart in raw:
        cart_id = cart["id"]
        user_id = cart["userId"]
        date = cart ["date"]
        for product in cart.get("products", []):
            rows.append({
                "cart_id": cart_id,
                "user_id": user_id,
                "cart_date": date,
                "product_id": product.get("productId"),
                "quantity": product.get("quantity"),
            })
    df = pd.DataFrame(rows)
    df["cart_id"]    = df["cart_id"].astype(int)
    df["user_id"]    = df["user_id"].astype(int)
    df["product_id"] = df["product_id"].astype(int)
    df["quantity"]   = df["quantity"].astype(int)
    return df

# Function to flatten nested JSON structures for USERS into tabular form.
# Removing sensitive PII information like street-level address and geolocation.
def flatten_users(raw: list[dict]) -> pd.DataFrame:
    rows = []
    for user in raw:
        address = user.pop("address", {})
        geo = address.pop("geolocation", {})
        name = user.pop("name",{})
        rows.append({
            "id": user.get("id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "first_ name": name.get("firstname"),
            "last_name": name.get("lastname"),
            "phone": user.get("phone"),
            "city": address.get("city"),
            "zipcode" : address.get("zipcode"),
            "geo_lat" : geo.get("lat"),
            "geo_long" : geo.get("long")
        })
    df = pd.DataFrame(rows)
    df["id"] = df["id"].astype(int)
    return df

# Function to load records to BigQuery database
def load_to_bigquery(df: pd.DataFrame, table_id: str, client:bigquery.Client)-> None:
    job_config = bigquery.LoadJobConfig(
        write_disposition = bigquery.WriteDisposition.WRITE_APPEND,
        autodetect = True,
    )
    log.info(f"Loading {len(df)} rows to {table_id}")
    job = client.load_table_from_dataframe(df, table_id, job_config = job_config)
    job.result()
    log.info(f" -> Loading complete. Rows in table: {client.get_table(table_id).num_rows}")

def run_pipeline():
    log.info("=" * 60)
    log.info("E-Commerce Data Ingestion Pipeline Started")
    log.info("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    raw_products = fetch_endpoint("products")
    df_products = flatten_products(raw_products)
    df_products = add_metadata(df_products)
    load_to_bigquery(df_products, TABLES["products"], client)

    raw_carts = fetch_endpoint("carts")
    df_carts = flatten_carts(raw_carts)
    df_carts = add_metadata(df_carts)
    load_to_bigquery(df_carts, TABLES["carts"], client)

    raw_users = fetch_endpoint("users")
    df_users = flatten_users(raw_users)
    df_users = add_metadata(df_users)
    load_to_bigquery(df_users, TABLES["users"], client)

    log.info("=" * 60)
    log.info("E-Commerce Data Ingestion Pipeline Completed")
    log.info("=" * 60)

if __name__ == "__main__":
    run_pipeline()