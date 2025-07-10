import pandas as pd
import numpy as np
import os
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account
import ast

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'data_exports', 'divvy_stations_data.csv')
divvy_stations = pd.read_csv(
    csv_path,
    header='infer'
)
################## Clean 
divvy_stations = divvy_stations.rename(columns={'id':'divvy_station_id'})
divvy_stations = divvy_stations.drop(columns=['short_name'])

# Keep only rows where status is 'In Service'
divvy_stations = divvy_stations[divvy_stations['status'] == 'In Service']


# Create WKT 'geometry' column using existing float columns
divvy_stations['geometry'] = divvy_stations.apply(
    lambda row: f"POINT({row['longitude']} {row['latitude']})"
    if pd.notnull(row['longitude']) and pd.notnull(row['latitude']) else None,
    axis=1
)

################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.divvy_stations.clean_divvy_stations_v2"

schema = [
    bigquery.SchemaField("divvy_station_id", "STRING"),
    bigquery.SchemaField("station_name", "STRING"),
    bigquery.SchemaField("total_docks", "INTEGER"),
    bigquery.SchemaField("docks_in_service", "INTEGER"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("latitude", "FLOAT"),
    bigquery.SchemaField("longitude", "FLOAT"),
    bigquery.SchemaField("location_type", "STRING"),
    bigquery.SchemaField("location_type", "STRING"),
    bigquery.SchemaField("geometry", "GEOGRAPHY")
]

# Define the job config
job_config = bigquery.LoadJobConfig(
    schema = schema,
    write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    divvy_stations, table_id, job_config=job_config
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
output_csv_path = os.path.join(output_dir, 'divvy_stations_cleaned.csv')

# Save the DataFrame to CSV
divvy_stations.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")