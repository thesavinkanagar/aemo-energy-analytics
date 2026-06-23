import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import os
import io

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="RAW"
    )

def download_aemo_data():
    print("📥 Downloading AEMO data...")

    regions = ["NSW1", "VIC1", "QLD1", "SA1", "TAS1"]
    months = [
        "202501","202502","202503","202504",
        "202505","202506","202507","202508",
        "202509","202510","202511","202512"
    ]

    all_dfs = []

    for month in months:
        for region in regions:
            url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{month}_{region}.csv"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    df = pd.read_csv(io.StringIO(response.text))
                    all_dfs.append(df)
                    print(f"  ✅ {month} {region} — {len(df)} rows")
                else:
                    print(f"  ⚠️  {month} {region} — skipped (status {response.status_code})")
            except Exception as e:
                print(f"  ❌ {month} {region} — error: {e}")

    if not all_dfs:
        raise Exception("No data downloaded. Check your internet connection.")

    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"\n📊 Total rows downloaded: {len(df_all):,}")
    return df_all

def clean_data(df):
    print("\n🧹 Cleaning data...")

    # Standardise column names to uppercase
    df.columns = [col.strip().upper().replace(" ", "_") for col in df.columns]

    # Parse datetime
    df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Cast numerics
    df["TOTALDEMAND"] = pd.to_numeric(df["TOTALDEMAND"], errors="coerce")
    df["RRP"] = pd.to_numeric(df["RRP"], errors="coerce")

    # Drop duplicates
    df = df.drop_duplicates()

    # Keep only expected columns in correct order
    df = df[["REGION", "SETTLEMENTDATE", "TOTALDEMAND", "RRP", "PERIODTYPE"]]

    print(f"  ✅ Clean rows: {len(df):,}")
    return df

def load_to_snowflake(df):
    print("\n🚀 Loading to Snowflake...")
    conn = get_connection()

    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name="RAW_GENERATION",
        database="ENERGY_DB",
        schema="RAW",
        overwrite=True
    )

    print(f"  ✅ Loaded {nrows:,} rows in {nchunks} chunks")
    conn.close()

if __name__ == "__main__":
    df = download_aemo_data()
    df = clean_data(df)
    load_to_snowflake(df)
    print("\n✅ Day 2 complete! Data is in Snowflake.")