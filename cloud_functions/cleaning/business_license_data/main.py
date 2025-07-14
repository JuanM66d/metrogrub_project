import os
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery

def clean_chicago_business_licenses(request):
    client = bigquery.Client()

    input_table = os.environ["INPUT_TABLE"]
    output_table = os.environ["OUTPUT_TABLE"]

    # Retrieve the raw data into a pandas DataFrame
    query = f"SELECT * FROM `{input_table}`"
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} rows from {input_table}")

    # Keep only the specified columns
    columns_to_keep = [
        'license_id',
        'doing_business_as_name',
        'legal_name',
        'business_activity_id',
        'license_description',
        'business_activity',
        'latitude',
        'longitude',
        'city',
        'state',
        'address',
        'zip_code',
        'location'
    ]

    df = df[columns_to_keep]

    # Remove rows with missing values in critical columns
    df = df.dropna(subset=['location', 'zip_code', 'business_activity'])
    # Remove rows where 'location' is the string "null"
    df = df[df['location'] != 'null']
    # Keep only rows where 'state' is 'IL'
    df = df[df['state'] == 'IL']
    # Remove rows where 'address' is '[REDACTED FOR PRIVACY]'
    df = df[df['address'] != '[REDACTED FOR PRIVACY]']
    # Remove duplicate rows based on 'license_id', keeping the first instance
    df = df.drop_duplicates(subset=['license_id'], keep='first')
    # Keep only rows where 'license_description' contains the word 'food' (case-insensitive)
    df = df[df['license_description'].str.contains('food', case=False, na=False)]

    # Convert 'location' column to BigQuery POINT WKT format
    def convert_to_point(location_str):
        try:
            loc_json = json.loads(location_str)
            coords = loc_json.get('coordinates', None)
            if coords and len(coords) == 2:
                lon, lat = coords
                return f"POINT({lon} {lat})"
            else:
                return None
        except Exception as e:
            return None

    df['location'] = df['location'].apply(convert_to_point)

    # Add in food_category column
    def categorize_food_place(row):
        desc = str(row['license_description']).lower()
        name_dba = str(row.get('doing_business_as_name', '')).lower()
        name_legal = str(row.get('legal_name', '')).lower()
        activity = str(row.get('business_activity', '')).lower()

        # Direct license-based categorization
        if 'mobile food' in desc:
            return 'food_truck'
        elif 'shared kitchen' in desc:
            return 'shared_kitchen'
        elif 'wholesale' in desc:
            return 'wholesale'
        elif 'special event' in desc:
            return 'event_food'
        elif 'pop-up' in desc:
            return 'pop_up'
        elif 'seasonal lakefront' in desc:
            return 'lakefront'

        # Business activity-based categorization
        if 'retail sales of general merchandise' in activity:
            return 'convenience_store'
        elif 'administrative commercial office' in activity:
            return 'office_cafeteria'

        # Combined name-based categorization
        full_name = f"{name_dba} {name_legal}"

        fast_food_keywords = [
            'raising cane', '7-eleven', 'pizza hut', 'wingstop', 'jimmy johns', 'dunkin',
            'potbelly', 'chick-fil-a', 'dominos', 'mcdonald', 'kentucky', 'kfc',
            'shake shack', 'burger king', 'taco bell', 'subway', 'wendy', 'popeyes'
        ]
        fine_dining_keywords = ['steakhouse', 'grill', 'bistro', 'chophouse', 'prime', 'fine dining']
        cafe_keywords = ['coffee', 'cafe', 'espresso', 'tea', 'starbucks']
        bar_keywords = ['bar', 'pub', 'tavern', 'lounge']

        if any(kw in full_name for kw in fast_food_keywords):
            return 'fast_food'
        elif any(kw in full_name for kw in fine_dining_keywords):
            return 'fine_dining'
        elif any(kw in full_name for kw in cafe_keywords):
            return 'cafe'
        elif any(kw in full_name for kw in bar_keywords):
            return 'bar'
        else:
            return 'restaurant'  # fallback

    # Apply the categorization function to create the 'food_category' column
    df['food_category'] = df.apply(categorize_food_place, axis=1)

    # Generate normally distributed random fake location score
    mean = 50      # center of distribution
    std_dev = 15   # spread
    df['fake_location_score'] = np.clip(np.random.normal(loc=mean, 
                                                        scale=std_dev, 
                                                        size=len(df)).round(), 1, 100).astype(int)

    # Write the cleaned DataFrame to the OUTPUT_TABLE in BigQuery, replacing existing data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrites the table
        schema=[
            bigquery.SchemaField("license_id", "STRING"),
            bigquery.SchemaField("doing_business_as_name", "STRING"),
            bigquery.SchemaField("legal_name", "STRING"),
            bigquery.SchemaField("license_description", "STRING"),
            bigquery.SchemaField("business_activity", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("address", "STRING"),
            bigquery.SchemaField("zip_code", "STRING"),
            bigquery.SchemaField("location", "GEOGRAPHY"),
            bigquery.SchemaField("food_category", "STRING"),
            bigquery.SchemaField("fake_location_score", "INTEGER")
        ]
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"
