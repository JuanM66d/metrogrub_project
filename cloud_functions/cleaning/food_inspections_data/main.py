import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_chicago_food_inspections(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} rows from {input_table}")

    col_to_keep = [
        'dba_name',
        'facility_type',
        'address',
        'city',
        'zip',
        'state',
        'latitude',
        'longitude',
        'location',
    ]

    df = df[col_to_keep]
    # remove rows where state is not IL
    df = df[df['state'] == 'IL']
    # Remove rows where location is null
    df = df[df['location'].notnull()]
    # Remove duplicate addresses (keep the first occurrence)
    df = df.drop_duplicates(subset=['address'])
    # remove rows where facility_type is null
    df = df[df['facility_type'].notnull()]

    def categorize_facility_type(ftype):
        ftype = ftype.lower()
        if any(kw in ftype for kw in ['restaurant', 'cafe', 'diner', 'bar', 'tavern', 'pub', 'coffee', 'brewery', 'ice cream', 'deli', 'food', 'candy', 'bakery']):
            return 'Food & Dining'
        elif any(kw in ftype for kw in ['grocery', 'market', 'liquor', 'retail']):
            return 'Retail & Grocery'
        elif any(kw in ftype for kw in ['school', 'college', 'university']):
            return 'Education'
        elif any(kw in ftype for kw in ['hospital', 'clinic', 'care', 'daycare', 'day care']):
            return 'Healthcare'
        elif any(kw in ftype for kw in ['gym', 'fitness', 'yoga']):
            return 'Recreation & Fitness'
        elif any(kw in ftype for kw in ['theater', 'movie', 'club', 'stadium', 'rooftop']):
            return 'Entertainment'
        elif any(kw in ftype for kw in ['hotel', 'motel']):
            return 'Hospitality'
        elif any(kw in ftype for kw in ['church', 'temple', 'mosque', 'synagogue']):
            return 'Religious'
        elif any(kw in ftype for kw in ['laundromat', 'office']):
            return 'Other'
        else:
            return 'Other'
        
    # Apply the categorization function to update the facility_type column
    df['facility_category'] = df['facility_type'].apply(categorize_facility_type)

    df = df[df['facility_category'] != 'Other']  # Filter out 'Other' category

    print(f"Categorized {len(df)} facility types")
    
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
            bigquery.SchemaField("dba_name", "STRING"),
            bigquery.SchemaField("facility_type", "STRING"),
            bigquery.SchemaField("facility_category", "STRING"),
            bigquery.SchemaField("address", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("zip", "STRING"),
            bigquery.SchemaField("state", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("location", "GEOGRAPHY")
        ],
        write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"