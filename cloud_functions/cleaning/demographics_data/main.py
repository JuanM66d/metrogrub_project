import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_chicago_demographics(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} rows from {input_table}")

    # Drop some columns 
    df = df.drop(['geography_type','record_id'],axis=1)
    # Keep only the zip codes that are not 'Chicago'
    df = df[df['zip_code'] != 'Chicago']

    # Write the cleaned DataFrame to the OUTPUT_TABLE in BigQuery, replacing existing data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrites the table if it exists
        autodetect=True  # Automatically detects schema from DataFrame
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"