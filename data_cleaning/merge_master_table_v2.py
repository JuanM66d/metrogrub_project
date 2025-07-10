import pandas as pd
import numpy as np
import os
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account
import ast
from shapely.wkt import loads as wkt_loads
import geopandas as gpd
from shapely.geometry import shape
import json

food_license = pd.read_csv(
    'data_outputs/food_licenses_cleaned.csv',
    dtype={'zip_code': str,'business_activity_id': str},  # force zip_code column to be string
    header='infer'
)

divvy_stations = pd.read_csv('data_outputs/divvy_stations_cleaned.csv',dtype={'bus_stop_id': str}, header='infer')
population_counts = pd.read_csv('data_outputs/population_counts_cleaned.csv', header='infer')
yearly_average = pd.read_csv('data_exports/yearly_average.csv', header='infer')
zoning_data = pd.read_csv('data_outputs/zoning_data_cleaned.csv', header='infer')
bus_stop = pd.read_csv('data_outputs/bus_stations_cleaned.csv', header='infer')

################## Merge
# Add boolean col (this is help in looker filtering food/bus_stop/divvy_station if needed)
food_license['is_food'] = 1
food_license['is_bus_stop'] = 0
food_license['is_divvy_station'] = 0

bus_stop['is_food'] = 0
bus_stop['is_bus_stop'] = 1
bus_stop['is_divvy_station'] = 0

divvy_stations['is_food'] = 0
divvy_stations['is_bus_stop'] = 0
divvy_stations['is_divvy_station'] = 1
divvy_stations_v2 = divvy_stations.drop(['total_docks','status','location_type','location_coordinates'],axis=1)

# Append point type data sources together
combined_df = pd.concat([food_license, bus_stop,divvy_stations_v2], ignore_index=True)

# Convert WKT string to shapely geometry
combined_df_v2 = combined_df.copy()
combined_df_v2['geometry'] = combined_df['geometry'].apply(wkt_loads)

combined_gdf_v2 = gpd.GeoDataFrame(combined_df_v2, geometry='geometry', crs='EPSG:4326')
zipcode = gpd.read_file('tl_2024_us_zcta520/tl_2024_us_zcta520.shp')
zipcode = zipcode.to_crs('EPSG:4326')

gdf_with_zip = gpd.sjoin(combined_gdf_v2, zipcode[['ZCTA5CE20', 'geometry']], how='left', predicate='intersects')
gdf_with_zip = gdf_with_zip.rename(columns={'ZCTA5CE20': 'zip_code_2'})

gdf_with_zip['zip_code_2'] = gdf_with_zip['zip_code_2'].astype(str)
population_counts['zip_code'] = population_counts['zip_code'].astype(str)

gdf_with_zip_v2 = gdf_with_zip.merge(
    population_counts,
    how='left',
    left_on='zip_code_2',
    right_on='zip_code'
)

zoning_data = zoning_data.rename(columns={'index_right': 'zoning_index'})
# First convert string to dict
zoning_data['geometry'] = zoning_data['geometry'].apply(json.loads)
zoning_data['geometry'] = zoning_data['geometry'].apply(shape)
zoning_data = gpd.GeoDataFrame(zoning_data, geometry='geometry')
zoning_data.set_crs("EPSG:4326", inplace=True)

if 'index_right' in gdf_with_zip_v2.columns:
    gdf_with_zip_v2 = gdf_with_zip_v2.drop(columns='index_right')

# Perform spatial join: points (left) within polygons (right)
gdf_with_zip_v3 = gpd.sjoin(
    gdf_with_zip_v2,      # left: points
    zoning_data,          # right: polygons
    how='left',           # keep all points
    predicate='within'    # or 'intersects' if appropriate
)

# --- Data Type Pre-processing for BigQuery Upload ---
# FIXED: Handle NaN values properly for BigQuery upload
# Convert to appropriate nullable types instead of converting everything to string

# Add debugging to see what's in the problematic columns
print("=== DEBUGGING DATA TYPES ===")
print(f"license_id column info:")
print(f"  Data type: {gdf_with_zip_v3['license_id'].dtype}")
print(f"  Sample values: {gdf_with_zip_v3['license_id'].head(10).tolist()}")
print(f"  Unique data types in license_id: {set(type(x).__name__ for x in gdf_with_zip_v3['license_id'].dropna())}")

# For string columns that should remain strings (expanded list based on schema)
string_columns = ['license_id', 'doing_business_as_name', 'legal_name', 'license_description', 
                 'business_activity', 'city', 'address', 'zip_code_x', 'location', 'food_category',
                 'bus_stop_id', 'street', 'cross_st', 'public_nam', 'divvy_station_id', 'station_name',
                 'zip_code_2', 'zip_code_y', 'zoning_id', 'zone_class', 'objectid', 'description',
                 'district_title', 'zoning_code_section', 'maximum_building_height', 'lot_area_per_unit',
                 'front_yard_setback', 'side_setback', 'rear_yard_setback', 'rear_yard_open_space',
                 'on_site_open_space', 'minimum_lot_area']

for col in string_columns:
    if col in gdf_with_zip_v3.columns:
        print(f"\nProcessing string {col}:")
        print(f"  Before: dtype={gdf_with_zip_v3[col].dtype}, sample={gdf_with_zip_v3[col].head(3).tolist()}")
        
        # Convert to string properly, handling all data types
        gdf_with_zip_v3[col] = gdf_with_zip_v3[col].astype(str)
        # Replace 'nan' string with None
        gdf_with_zip_v3[col] = gdf_with_zip_v3[col].replace({'nan': None, 'None': None})
        # Convert to nullable string
        gdf_with_zip_v3[col] = gdf_with_zip_v3[col].astype('string')
        
        print(f"  After: dtype={gdf_with_zip_v3[col].dtype}, sample={gdf_with_zip_v3[col].head(3).tolist()}")

# For numeric columns that should remain numeric
numeric_columns = ['business_activity_id', 'latitude', 'longitude', 'location_score', 
                  'docks_in_service', 'year', 'population_total', 'population_0_to_17',
                  'population_18_to_29', 'population_30_to_39', 'population_40_to_49',
                  'population_50_to_59', 'population_60_to_69', 'population_70_to_79',
                  'population_80', 'population_female', 'population_male', 'population_latinx',
                  'population_asian', 'population_black', 'population_white', 'population_other',
                  'index_right', 'shape_area', 'shape_len', 'floor_area_ratio']

for col in numeric_columns:
    if col in gdf_with_zip_v3.columns:
        print(f"\nProcessing numeric {col}:")
        print(f"  Before: dtype={gdf_with_zip_v3[col].dtype}")
        # Ensure numeric columns remain numeric with proper NaN handling
        gdf_with_zip_v3[col] = pd.to_numeric(gdf_with_zip_v3[col], errors='coerce')
        print(f"  After: dtype={gdf_with_zip_v3[col].dtype}")

# Handle edit_date properly
if 'edit_date' in gdf_with_zip_v3.columns:
    print(f"\nProcessing edit_date:")
    print(f"  Before: dtype={gdf_with_zip_v3['edit_date'].dtype}")
    gdf_with_zip_v3['edit_date'] = pd.to_datetime(gdf_with_zip_v3['edit_date'], errors='coerce')
    print(f"  After: dtype={gdf_with_zip_v3['edit_date'].dtype}")

# Handle boolean columns
boolean_columns = ['is_food', 'is_bus_stop', 'is_divvy_station', 'restaurant_allowed']
for col in boolean_columns:
    if col in gdf_with_zip_v3.columns:
        print(f"\nProcessing boolean {col}:")
        print(f"  Before: dtype={gdf_with_zip_v3[col].dtype}")
        gdf_with_zip_v3[col] = gdf_with_zip_v3[col].astype('boolean')
        print(f"  After: dtype={gdf_with_zip_v3[col].dtype}")

# FIXED: Handle geometry column properly for BigQuery
# Convert geometry to WKT string for BigQuery GEOGRAPHY type
if 'geometry' in gdf_with_zip_v3.columns:
    print(f"\nProcessing geometry:")
    print(f"  Before: dtype={gdf_with_zip_v3['geometry'].dtype}")
    print(f"  Sample values: {gdf_with_zip_v3['geometry'].head(3).tolist()}")
    
    # Make sure we're working with valid geometries
    gdf_with_zip_v3['geometry'] = gdf_with_zip_v3['geometry'].apply(
        lambda geom: geom.wkt if geom is not None and hasattr(geom, 'wkt') else None
    )
    print(f"  After: dtype={gdf_with_zip_v3['geometry'].dtype}")
    print(f"  Sample values: {gdf_with_zip_v3['geometry'].head(3).tolist()}")

# Final data type check
print("\n=== FINAL DATA TYPES ===")
print(gdf_with_zip_v3.dtypes)
print(f"\nDataFrame shape: {gdf_with_zip_v3.shape}")
print(f"Columns: {list(gdf_with_zip_v3.columns)}")

################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.master_table.master_table_draft"

# FIXED: Schema with proper nullable types
schema = [
    bigquery.SchemaField("license_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("doing_business_as_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("legal_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("business_activity_id", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("license_description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("business_activity", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("latitude", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("longitude", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("zip_code_x", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("geometry", "GEOGRAPHY", mode="NULLABLE"),
    bigquery.SchemaField("food_category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("location_score", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("is_food", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("is_bus_stop", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("is_divvy_station", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("bus_stop_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("street", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("cross_st", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("public_nam", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("divvy_station_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("station_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("docks_in_service", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("zip_code_2", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("year", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("zip_code_y", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("population_total", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_0_to_17", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_18_to_29", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_30_to_39", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_40_to_49", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_50_to_59", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_60_to_69", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_70_to_79", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_80", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_female", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_male", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_latinx", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_asian", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_black", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_white", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("population_other", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("index_right", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("zoning_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("zone_class", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("edit_date", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("shape_area", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("shape_len", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("objectid", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("district_title", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("zoning_code_section", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("floor_area_ratio", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("maximum_building_height", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("lot_area_per_unit", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("front_yard_setback", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("side_setback", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("rear_yard_setback", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("rear_yard_open_space", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("on_site_open_space", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("minimum_lot_area", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("restaurant_allowed", "BOOLEAN", mode="NULLABLE")
]

# Define the job config
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    gdf_with_zip_v3, table_id, job_config=job_config
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
output_csv_path = os.path.join(output_dir, 'master_table_draft.csv')

# Save the DataFrame to CSV
gdf_with_zip_v3.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")