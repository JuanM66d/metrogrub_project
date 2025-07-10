import pandas as pd
import numpy as np
import os
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'data_exports', 'cta_bus_stations_data.csv')
bus_data = pd.read_csv(
    csv_path,
    header='infer'
)
################## Clean 
#Drop columns
bus_data_v2 = bus_data.drop(['dir','pos','routesstpg'],axis=1)
bus_data_v2 = bus_data_v2.rename(columns={'systemstop':'bus_stop_id'})

#Cast as a point 
bus_data_v2['geometry'] = bus_data_v2.apply(
    lambda row: f"POINT({row['longitude']} {row['latitude']})" 
    if pd.notnull(row['longitude']) and pd.notnull(row['latitude']) 
    else None,
    axis=1
)

################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.cta_bus_stations.clean_bus_stations_v2"

schema = [
    bigquery.SchemaField("longitude", "FLOAT"),
    bigquery.SchemaField("latitude", "FLOAT"),
    bigquery.SchemaField("bus_stop_id", "INTEGER"),
    bigquery.SchemaField("street", "STRING"),
    bigquery.SchemaField("cross_st", "STRING"),
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("public_nam", "STRING"),
    bigquery.SchemaField("geometry", "GEOGRAPHY")
]

# Define the job config
job_config = bigquery.LoadJobConfig(
    schema = schema,
    write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    bus_data_v2, table_id, job_config=job_config
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
output_csv_path = os.path.join(output_dir, 'bus_stations_cleaned.csv')

# Save the DataFrame to CSV
bus_data_v2.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")