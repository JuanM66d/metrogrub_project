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

    df = df.rename(columns={'doing_business_as_name': 'entity_name'})
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
    # Keep only rows where 'license_description' contains the word 'food' or 'consumption' (case-insensitive)
    df = df[df['license_description'].str.contains('food|consumption', case=False, na=False)]

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
        desc = str(row.get('license_description', '')).lower()
        name = str(row.get('entity_name', '')).lower()
        text = f"{desc} {name}"  # combine both fields

        all_food_keywords = ['panda express','raising cane', 'pizza hut', 'wingstop', 'jimmy johns', 'dunkin',
            'potbelly', 'chick-fil-a', 'dominos', 'mcdonald', 'kentucky', 'kfc',
            'shake shack', 'burger king', 'taco bell', 'subway', 'wendy', 'popeyes', 'steak','steakhouse', 
            'bistro', 'chophouse', 'prime', 'fine dining', 'coffee', 'cafe', 'espresso', 'tea', 
            'starbucks', 'bakery', 'pastry', 'patisserie', 'bar', 'pub', 'tavern', 'lounge', 
            'brewery', 'wine', 'cocktail', 'taproom', 'restaurant', 'pizza', 'burger']
        fast_food_keywords = [
            'raising cane', 'pizza hut', 'wingstop', 'jimmy johns', 'dunkin',
            'potbelly', 'chick-fil-a', 'dominos', 'mcdonald', 'kentucky', 'kfc',
            'shake shack', 'burger king', 'taco bell', 'subway', 'wendy', 'popeyes', 'panda express'
        ]
        fine_dining_keywords = ['steak', 'steakhouse', 'bistro', 'chophouse', 'prime', 'fine dining']
        cafe_keywords = ['coffee', 'cafe', 'espresso', 'tea', 'starbucks', 'bakery', 'pastry', 'patisserie']
        bar_keywords = ['bar', 'pub', 'tavern', 'lounge', 'brewery', 'wine', 'cocktail', 'taproom', 'beer']


        text = text.lower()

        if any(kw in text for kw in ['grocery', 'market', 'liquor', 'store', 'drug', 'drug store', 'convenience', 'supermarket', 'wholesale', '7-eleven', 'cvs', 'walgreens']):
            return 'retail_grocery'
        elif any(kw in text for kw in ['school', 'college', 'university']):
            return 'school'
        elif any(kw in text for kw in ['hospital', 'clinic', 'care', 'daycare', 'day care']):
            return 'healthcare'
        elif any(kw in text for kw in ['gym', 'fitness', 'yoga']):
            return 'fitness'
        elif any(kw in text for kw in ['theater', 'movie', 'club', 'stadium', 'rooftop']):
            return 'entertainment'
        elif any(kw in text for kw in ['hotel', 'motel', 'hospitality']):
            return 'hospitality'
        elif any(kw in text for kw in ['church', 'temple', 'mosque', 'synagogue']):
            return 'religious'
        elif any(kw in text for kw in all_food_keywords):
            if any(kw in text for kw in fast_food_keywords):
                return 'fast_food'
            elif any(kw in text for kw in fine_dining_keywords):
                return 'fine_dining'
            elif any(kw in text for kw in cafe_keywords):
                return 'cafe'
            elif any(kw in text for kw in bar_keywords):
                return 'bar'
            else:
                return 'restaurant'
        else: 
            return 'other'

    # Apply the categorization function to create the 'food_category' column
    df['category'] = df.apply(categorize_food_place, axis=1)

    # Set 'is_food' to True if category is one of the food-related types
    food_categories = ['fast_food', 'fine_dining', 'cafe', 'bar', 'restaurant']
    df['is_food'] = df['category'].isin(food_categories).astype(int)
    df['is_business'] = (df['is_food'] == 0).astype(int)

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
            bigquery.SchemaField("is_food", "INTEGER"),
            bigquery.SchemaField("is_business", "INTEGER"),
            bigquery.SchemaField("license_id", "STRING"),
            bigquery.SchemaField("entity_name", "STRING"),
            bigquery.SchemaField("legal_name", "STRING"),
            bigquery.SchemaField("license_description", "STRING"),
            bigquery.SchemaField("business_activity", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("address", "STRING"),
            bigquery.SchemaField("zip_code", "STRING"),
            bigquery.SchemaField("location", "GEOGRAPHY"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("fake_location_score", "INTEGER")
        ]
    )

    job = client.load_table_from_dataframe(df, output_table, job_config=job_config)
    job.result()  # Wait for the load job to complete

    print(f"Successfully loaded cleaned data to {output_table} (table replaced)")

    return f"Loaded {len(df)} cleaned rows to {output_table}"
