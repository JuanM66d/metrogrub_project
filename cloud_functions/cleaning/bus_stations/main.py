import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_cta_bus_stations(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    # Drop/rename some columns
    df = df.drop(['dir','pos','routesstpg'],axis=1)
    df = df.rename(columns={'systemstop':'bus_stop_id', 'public_nam': 'entity_name'})

    # Cast as a point
    df['location'] = df.apply(
        lambda row: f"POINT({row['longitude']} {row['latitude']})" 
        if pd.notnull(row['longitude']) and pd.notnull(row['latitude']) 
        else None,
        axis=1
    )

    # Define the job config
    job_config = bigquery.LoadJobConfig(
        schema = [
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("bus_stop_id", "STRING"),
            bigquery.SchemaField("street", "STRING"),
            bigquery.SchemaField("cross_st", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("entity_name", "STRING"),
            bigquery.SchemaField("location", "GEOGRAPHY")
        ],
        write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"