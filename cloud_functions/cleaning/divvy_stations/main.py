import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_divvy_station_data(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} rows from {input_table}")

    # rename columns and drop unnecessary ones
    df = df.rename(columns={'id':'divvy_station_id', 'station_name':'entity_name'})
    df = df.drop(columns=['short_name'])
    # Keep only rows where status is 'In Service'
    df = df[df['status'] == 'In Service']

    # Create WKT 'location' column using existing coordinate columns
    df['location'] = df.apply(
        lambda row: f"POINT({row['longitude']} {row['latitude']})"
        if pd.notnull(row['longitude']) and pd.notnull(row['latitude']) else None,
        axis=1
    )

    # Write the cleaned DataFrame to the OUTPUT_TABLE in BigQuery, replacing existing data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrites the table if it exists
        schema = [
            bigquery.SchemaField("divvy_station_id", "STRING"),
            bigquery.SchemaField("entity_name", "STRING"),
            bigquery.SchemaField("total_docks", "INTEGER"),
            bigquery.SchemaField("docks_in_service", "INTEGER"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("location_type", "STRING"),
            bigquery.SchemaField("location", "GEOGRAPHY")
        ]
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"