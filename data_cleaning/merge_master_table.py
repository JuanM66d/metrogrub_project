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

gdf_with_zip_v3['geometry'] = gdf_with_zip_v3['geometry'].apply(lambda geom: geom.wkt if geom else None)

# --- Data Type Pre-processing for BigQuery Upload ---
# Convert 'license_id' to string, handling NaN values
# Fill NaN with None, then convert to object type (which is flexible for strings and None)
gdf_with_zip_v3['license_id'] = gdf_with_zip_v3['license_id'].replace({np.nan: None}).astype(str) # Convert to string after handling NaN

# Convert 'zoning_id' to string, handling NaN values
gdf_with_zip_v3['zoning_id'] = gdf_with_zip_v3['zoning_id'].replace({np.nan: None}).astype(str)

# Convert 'objectid' to string, handling NaN values, as the schema is FLOAT
# If it's truly an ID, STRING or NUMERIC is better. For now, converting to string
# to avoid float precision issues if it's an ID.
gdf_with_zip_v3['objectid'] = gdf_with_zip_v3['objectid'].replace({np.nan: None}).astype(str)

# Ensure 'edit_date' is in a format BigQuery TIMESTAMP can understand.
# Convert to datetime, then to string in ISO format.
# Handle potential NaT (Not a Time) values by converting them to None.
gdf_with_zip_v3['edit_date'] = pd.to_datetime(gdf_with_zip_v3['edit_date'], errors='coerce')
gdf_with_zip_v3['edit_date'] = gdf_with_zip_v3['edit_date'].dt.strftime('%Y-%m-%d %H:%M:%S.%f').replace({np.nan: None})
################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.master_table.master_table_draft"

schema = schema = schema = schema = [
    bigquery.SchemaField("license_id", "STRING"),
    bigquery.SchemaField("doing_business_as_name", "STRING"),
    bigquery.SchemaField("legal_name", "STRING"),
    bigquery.SchemaField("business_activity_id", "FLOAT"),
    bigquery.SchemaField("license_description", "STRING"),
    bigquery.SchemaField("business_activity", "STRING"),
    bigquery.SchemaField("latitude", "FLOAT"),
    bigquery.SchemaField("longitude", "FLOAT"),
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("address", "STRING"),
    bigquery.SchemaField("zip_code_x", "STRING"),
    bigquery.SchemaField("location", "STRING"),
    bigquery.SchemaField("geometry", "GEOGRAPHY"),
    bigquery.SchemaField("food_category", "STRING"),
    bigquery.SchemaField("location_score", "FLOAT"),
    bigquery.SchemaField("is_food", "BOOLEAN"),
    bigquery.SchemaField("is_bus_stop", "BOOLEAN"),
    bigquery.SchemaField("is_divvy_station", "BOOLEAN"),
    bigquery.SchemaField("bus_stop_id", "STRING"),
    bigquery.SchemaField("street", "STRING"),
    bigquery.SchemaField("cross_st", "STRING"),
    bigquery.SchemaField("public_nam", "STRING"),
    bigquery.SchemaField("divvy_station_id", "STRING"),
    bigquery.SchemaField("station_name", "STRING"),
    bigquery.SchemaField("docks_in_service", "FLOAT"),
    bigquery.SchemaField("zip_code_2", "STRING"),
    bigquery.SchemaField("year", "FLOAT"),
    bigquery.SchemaField("zip_code_y", "STRING"),
    bigquery.SchemaField("population_total", "FLOAT"),
    bigquery.SchemaField("population_0_to_17", "FLOAT"),
    bigquery.SchemaField("population_18_to_29", "FLOAT"),
    bigquery.SchemaField("population_30_to_39", "FLOAT"),
    bigquery.SchemaField("population_40_to_49", "FLOAT"),
    bigquery.SchemaField("population_50_to_59", "FLOAT"),
    bigquery.SchemaField("population_60_to_69", "FLOAT"),
    bigquery.SchemaField("population_70_to_79", "FLOAT"),
    bigquery.SchemaField("population_80", "FLOAT"),
    bigquery.SchemaField("population_female", "FLOAT"),
    bigquery.SchemaField("population_male", "FLOAT"),
    bigquery.SchemaField("population_latinx", "FLOAT"),
    bigquery.SchemaField("population_asian", "FLOAT"),
    bigquery.SchemaField("population_black", "FLOAT"),
    bigquery.SchemaField("population_white", "FLOAT"),
    bigquery.SchemaField("population_other", "FLOAT"),
    bigquery.SchemaField("index_right", "FLOAT"),
    bigquery.SchemaField("zoning_id", "STRING"), # Changed to STRING in schema
    bigquery.SchemaField("zone_class", "STRING"),
    bigquery.SchemaField("edit_date", "TIMESTAMP"),
    bigquery.SchemaField("shape_area", "FLOAT"),
    bigquery.SchemaField("shape_len", "FLOAT"),
    bigquery.SchemaField("objectid", "STRING"), # Changed to STRING in schema
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("district_title", "STRING"),
    bigquery.SchemaField("zoning_code_section", "STRING"),
    bigquery.SchemaField("floor_area_ratio", "FLOAT"),
    bigquery.SchemaField("maximum_building_height", "STRING"),
    bigquery.SchemaField("lot_area_per_unit", "STRING"),
    bigquery.SchemaField("front_yard_setback", "STRING"),
    bigquery.SchemaField("side_setback", "STRING"),
    bigquery.SchemaField("rear_yard_setback", "STRING"),
    bigquery.SchemaField("rear_yard_open_space", "STRING"),
    bigquery.SchemaField("on_site_open_space", "STRING"),
    bigquery.SchemaField("minimum_lot_area", "STRING"),
    bigquery.SchemaField("restaurant_allowed", "BOOLEAN")
]


# Define the job config
job_config = bigquery.LoadJobConfig(
    schema = schema,
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