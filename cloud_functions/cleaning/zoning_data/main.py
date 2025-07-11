import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_chicago_zoning(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} rows from {input_table}")

    # Select columns to keep
    col_to_keep = [
        'geometry',
        'zoning_id',
        'zone_class',
        'edit_date',
        'shape_area',
        'shape_len',
        'objectid'
    ]
    df = df[col_to_keep]
    
     #Add a boolean column for zone_class cols that can have restaurants
    def add_restaurant_allowed(df):
        licenses = ["B1", "B2", "B3", "C1", "C2", "C3", "DC", "DX", "DS", "M1", "M2", "M3","PMD"]
        pattern = '|'.join(licenses)
        df['restaurant_allowed'] = np.where(df['zone_class'].str.contains(pattern, na=False), 1, 0)
        return df
    
    df = add_restaurant_allowed(df)

    # Write the cleaned DataFrame to the OUTPUT_TABLE in BigQuery, replacing existing data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrites the table if it exists
        autodetect=True
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"