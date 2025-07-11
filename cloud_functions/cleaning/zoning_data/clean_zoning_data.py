import pandas as pd
import numpy as np
import os
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account

script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")
csv_path = os.path.join(script_dir, 'data_exports', 'zoning_data.csv')
zoning_data = pd.read_csv(
    csv_path,
    header='infer'
)

csv_path2 = os.path.join(script_dir, 'data_exports', 'zoning-code-summary-district-types.csv')
zoning_details = pd.read_csv(
    csv_path2,
    header='infer'
)
################## Clean 
# Drop zone_type & old_description
zoning_details_v2 = zoning_details.drop(['zone_type','old_description','old_zoning_ordinance_code'],axis=1)
# rename columns
zoning_details_v2 = zoning_details_v2.rename(columns={
    'district_type_code': 'zone_class',
    'juan_description': 'description'
})

# Select columns to keep
col_to_keep = ['geometry',
'zoning_id',
'zone_class',
'edit_date',
'shape_area',
'shape_len',
'objectid'
]
zoning_data_v2 = zoning_data[col_to_keep]
# Left join zoning_data with zoning_details
zoning_data_v3 = pd.merge(zoning_data_v2, zoning_details_v2, on='zone_class', how='left')

# Add a boolean column for zone_class cols that can have restaurants
def add_restaurant_allowed(df):
    licenses = ["B1", "B2", "B3", "C1", "C2", "C3", "DC", "DX", "DS", "M1", "M2", "M3","PMD"]
    pattern = '|'.join(licenses)
    df['restaurant_allowed'] = np.where(df['zone_class'].str.contains(pattern, na=False), 1, 0)
    return df

zoning_data_v4 = add_restaurant_allowed(zoning_data_v3)

zoning_data_v4

################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.chicago_zoning.clean_zoning_data_v4"

# Define the job config
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
    autodetect=True                      # Automatically detects schema from DataFrame
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    zoning_data_v4, table_id, job_config=job_config
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
output_csv_path = os.path.join(output_dir, 'zoning_data_cleaned.csv')

# Save the DataFrame to CSV
zoning_data_v4.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")