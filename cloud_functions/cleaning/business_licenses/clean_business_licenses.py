import pandas as pd
import numpy as np
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import json
from shapely.geometry import shape

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'data_exports', 'active_business_licenses.csv')
business_license = pd.read_csv(
    csv_path,
    dtype={'zip_code': str},  # force zip_code column to be string
    header='infer'
)

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

# Select only the desired columns
business_license_v2 = business_license[columns_to_keep]

# Remove rows with no location data, no zip code, no buziness_activity
business_license_v2 = business_license_v2[business_license_v2['location'].notna()]
business_license_v2 = business_license_v2[business_license_v2['zip_code'].notna()]
business_license_v2 = business_license_v2[business_license_v2['business_activity'].notna()]

def geojson_to_point(loc):
    try:
        if pd.isnull(loc) or loc == '':
            return None
        return shape(json.loads(loc))
    except Exception:
        return None

business_license_v2['geometry'] = business_license_v2['location'].apply(geojson_to_point)

# Replace redacted in address with NaN value
business_license_v2['address'] = business_license_v2['address'].replace(r'\[REDACTED.*\]', np.nan, regex=True)

# Remove businesses that are located outside of IL (check shows a lot of debt collection licenses)
business_license_v2 = business_license_v2[business_license_v2['state'] == 'IL']

# Drop State col after filtering 
business_license_v2 = business_license_v2.drop(columns=['state'])

################## Split into food table 
# Filter for food
business_license_v2_food = business_license_v2[
    business_license_v2['license_description'].str.contains('food', case=False, na=False)
]

# Remove duplicates of same biz license_id (keep only first one)
business_license_v3_food = business_license_v2_food.drop_duplicates(subset='license_id', keep='first')

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
    cafe_keywords = ['coffee', 'cafe', 'espresso', 'tea']
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
 
    
business_license_v4_food = business_license_v3_food.copy()
business_license_v4_food['food_category'] = business_license_v3_food.apply(categorize_food_place, axis=1)

# Generate normally distributed random location score
mean = 50      # center of distribution
std_dev = 15   # spread
business_license_v4_food['location_score'] = np.clip(np.random.normal(loc=mean, 
                                                                      scale=std_dev, 
                                                                      size=len(business_license_v4_food)).round(), 1, 100
).astype(int)

################## Split into hotel table 

# Filters business_activity rows for 'hotel' string
# business_license_v2_hotel = business_license_v2[
#     business_license_v2['license_description'].str.contains('hotel', case=False, na=False)
# ]

# # Remove duplicated of license_id
# business_license_v2_hotel = business_license_v2_hotel.drop_duplicates(subset='license_id', keep='first')

################## Upload back into big query
schema = [
    bigquery.SchemaField("license_id", "INTEGER"),
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
    bigquery.SchemaField("geometry", "GEOGRAPHY"),
    bigquery.SchemaField("food_category", "STRING"),
    bigquery.SchemaField("location_score", "INTEGER")
    
]
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.chicago_active_business_licenses.business_licenses_v4_food_clean"

# Define the job config
job_config = bigquery.LoadJobConfig(
    schema = schema,
    write_disposition="WRITE_TRUNCATE"  # Overwrites the table if it exists
    # autodetect=True                      # Automatically detects schema from DataFrame
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    business_license_v4_food, table_id, job_config=job_config
)

# Wait for the job to complete
job.result()

print(f"✅ DataFrame uploaded to {table_id}")

################ Download a backup
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path for the data_outputs folder
output_dir = os.path.join(script_dir, 'data_outputs')

# Create the data_outputs directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define the full path for the output CSV file
output_csv_path = os.path.join(output_dir, 'food_licenses_cleaned.csv')

# Save the DataFrame to CSV
business_license_v4_food.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")