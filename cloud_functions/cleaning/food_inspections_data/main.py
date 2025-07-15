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
    # Rename columns for consistency
    df = df.rename(columns={'dba_name': 'doing_business_as_name', 'zip': 'zip_code'})
    # remove rows where state is not IL
    df = df[df['state'] == 'IL']
    # Remove rows where location is null
    df = df[df['location'].notnull()]
    # Remove duplicate addresses (keep the first occurrence)
    df = df.drop_duplicates(subset=['address'])
    # remove rows where facility_type is null
    df = df[df['facility_type'].notnull()]

    def categorize_facility_type(ftype):
        all_food_keywords = ['raising cane', '7-eleven', 'pizza hut', 'wingstop', 'jimmy johns', 'dunkin',
            'potbelly', 'chick-fil-a', 'dominos', 'mcdonald', 'kentucky', 'kfc',
            'shake shack', 'burger king', 'taco bell', 'subway', 'wendy', 'popeyes', 'steakhouse', 
            'bistro', 'chophouse', 'prime', 'fine dining', 'coffee', 'cafe', 'espresso', 'tea', 
            'starbucks', 'bakery', 'pastry', 'patisserie', 'bar', 'pub', 'tavern', 'lounge', 
            'brewery', 'wine', 'cocktail', 'taproom']
        fast_food_keywords = [
            'raising cane', '7-eleven', 'pizza hut', 'wingstop', 'jimmy johns', 'dunkin',
            'potbelly', 'chick-fil-a', 'dominos', 'mcdonald', 'kentucky', 'kfc',
            'shake shack', 'burger king', 'taco bell', 'subway', 'wendy', 'popeyes'
        ]
        fine_dining_keywords = ['steakhouse', 'bistro', 'chophouse', 'prime', 'fine dining']
        cafe_keywords = ['coffee', 'cafe', 'espresso', 'tea', 'starbucks', 'bakery', 'pastry', 'patisserie']
        bar_keywords = ['bar', 'pub', 'tavern', 'lounge', 'brewery', 'wine', 'cocktail', 'taproom']


        ftype = ftype.lower()
        if any(kw in ftype for kw in ['grocery', 'market', 'liquor', 'retail', 'drug', 'drug store', 'convenience', 'supermarket', 'wholesale']):
            return 'retail_grocery'
        elif any(kw in ftype for kw in ['school', 'college', 'university']):
            return 'school'
        elif any(kw in ftype for kw in ['hospital', 'clinic', 'care', 'daycare', 'day care']):
            return 'healthcare'
        elif any(kw in ftype for kw in ['gym', 'fitness', 'yoga']):
            return 'fitness'
        elif any(kw in ftype for kw in ['theater', 'movie', 'club', 'stadium', 'rooftop']):
            return 'entertainment'
        elif any(kw in ftype for kw in ['hotel', 'motel']):
            return 'hospitality'
        elif any(kw in ftype for kw in ['church', 'temple', 'mosque', 'synagogue']):
            return 'religious'
        if any(kw in ftype for kw in all_food_keywords):
            if any(kw in ftype for kw in fast_food_keywords):
                return 'fast_food'
            elif any(kw in ftype for kw in fine_dining_keywords):
                return 'fine_dining'
            elif any(kw in ftype for kw in cafe_keywords):
                return 'cafe'
            elif any(kw in ftype for kw in bar_keywords):
                return 'bar'
            else:
                return 'restaurant'
        else:
            return 'Other'
        
    # Apply the categorization function to update the facility_type column
    df['category'] = df['facility_type'].apply(categorize_facility_type)
    # Set 'is_food' to True if category is one of the food-related types
    food_categories = ['fast_food', 'fine_dining', 'cafe', 'bar', 'restaurant']
    df['is_food'] = df['category'].isin(food_categories).astype(int)
    df['is_business'] = (df['is_food'] == 0).astype(int)


    df = df[df['category'] != 'Other']  # Filter out 'Other' category

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
            bigquery.SchemaField("doing_business_as_name", "STRING"),
            bigquery.SchemaField("facility_type", "STRING"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("address", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("zip_code", "STRING"),
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