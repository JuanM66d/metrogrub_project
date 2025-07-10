"""
Cloud Function entry-point:
  • Reads two files from GCS with google-cloud-storage
  • Generates synthetic foot-traffic
  • Loads the DataFrame into BigQuery with google-cloud-bigquery
"""

import io
import sys
import tempfile
from typing import List, Tuple

import pandas as pd
import numpy as np
import geopandas as gp
from shapely.geometry import Point
from google.cloud import storage, bigquery
import pyarrow


# ───────────────────────────────────────── Helper functions ──────────────────────────────────────────

def get_block_type_from_zoning(
    latitude: float,
    longitude: float,
    zoning_gdf: gp.GeoDataFrame
) -> int | None:
    point = Point(longitude, latitude)  # (lon, lat)

    # spatial index speeds things up after first access
    _ = zoning_gdf.sindex  

    for _, row in zoning_gdf.iloc[list(zoning_gdf.sindex.intersection(point.bounds))].iterrows():
        if row.geometry.contains(point):
            z = row["zone_class"].strip()
            if z.startswith("R") or z.startswith("M"):
                return 0          # Residential / Manufacturing
            if z.startswith(("B", "C")):
                return 1          # Business / Commercial
            if z.startswith(("D", "DC")):
                return 2          # Downtown / High-traffic
            return 1
    return None


def generate_yearly_average_foot_traffic(
    locations: List[Tuple[float, float]],
    zoning_gdf: gp.GeoDataFrame
) -> pd.DataFrame:
    rng = np.random.default_rng()
    rows = []

    for lat, lon in locations:
        block = get_block_type_from_zoning(lat, lon, zoning_gdf)
        if block is None:
            block = rng.choice([0, 1, 2], p=[0.50, 0.35, 0.15])

        yearly = (
            rng.integers(2000, 8001) if block == 2 else
            rng.integers(300, 1801)  if block == 1 else
            rng.integers(50, 501)
        )

        if rng.random() < 0.05:                      # occasional outlier
            yearly = (
                rng.integers(8000, 12001) if block == 2 else
                rng.integers(1800, 3001) if block == 1 else
                rng.integers(500, 1001)
            )
        rows.append((lat, lon, yearly))

    return pd.DataFrame(rows,
                        columns=["latitude", "longitude", "yearly_average_foot_traffic"])


# ─────────────────────────────────────────── main() ──────────────────────────────────────────────────

def main(request):
    BUCKET             = "foot_traffic_gen_resources"
    LOC_FILE           = "chicago_traffic_counts_raw.csv"
    ZONE_FILE          = "Chicago_Zoning_Data.geojson"

    PROJECT_ID         = "purple-25-gradient-20250605"
    DATASET_ID         = "foot_traffic_chicago"
    TABLE_ID           = "yearly_average"

    storage_client = storage.Client()
    bucket         = storage_client.bucket(BUCKET)

    # --- Load CSV directly into pandas ---
    loc_blob = bucket.blob(LOC_FILE)
    if not loc_blob.exists():
        sys.exit(f"ERROR: blob gs://{BUCKET}/{LOC_FILE} not found")

    loc_bytes = loc_blob.download_as_bytes()
    locations_df = (
        pd.read_csv(io.BytesIO(loc_bytes))[["Latitude", "Longitude"]]
          .round(4)
          .dropna()
          .drop_duplicates()
    )

    # --- Load GeoJSON into GeoPandas ---
    zone_blob = bucket.blob(ZONE_FILE)
    if not zone_blob.exists():
        sys.exit(f"ERROR: blob gs://{BUCKET}/{ZONE_FILE} not found")

    with tempfile.NamedTemporaryFile(suffix=".geojson") as tmp:
        zone_blob.download_to_file(tmp)
        tmp.flush()
        zoning_gdf = gp.read_file(tmp.name)

    # --- Generate synthetic traffic ---
    foot_traffic_df = generate_yearly_average_foot_traffic(
        list(locations_df.itertuples(index=False, name=None)),
        zoning_gdf,
    )

    # --- Write DataFrame to BigQuery ---
    bq_client  = bigquery.Client(project=PROJECT_ID)
    table_ref  = bq_client.dataset(DATASET_ID).table(TABLE_ID)

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )

    job = bq_client.load_table_from_dataframe(
        foot_traffic_df, table_ref, job_config=job_config
    )
    job.result()                       # wait for completion
    print(f"Loaded {job.output_rows} rows into {PROJECT_ID}:{DATASET_ID}.{TABLE_ID}")
    return ("Done", 200)
