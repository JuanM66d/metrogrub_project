import pandas as pd
import numpy as np
import os
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'data_exports', 'population_counts.csv')
population_counts = pd.read_csv(
    csv_path,
    header='infer'
)
################## Clean 
population_counts_v2 = population_counts.drop(['geography_type','record_id'],axis=1)
population_counts_v2 = population_counts_v2[population_counts['zip_code'] != 'Chicago']
population_counts_v3 = population_counts_v2[population_counts_v2['year']==2021]

################## Upload back into big query
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, 'purple-25-gradient-20250605-9a86eb7ca8de.json')

creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds,project="purple-25-gradient-20250605")

# Define destination table: dataset_id.table_name (make in big query first)
table_id = "purple-25-gradient-20250605.chicago_demographics.clean_population_counts_v3"

# Define the job config
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists
    autodetect=True                      # Automatically detects schema from DataFrame
)

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(
    population_counts_v3, table_id, job_config=job_config
)

# Wait for the job to complete
job.result()

print(f"✅ DataFrame uploaded to {table_id}")
print(population_counts_v3)
################ Download a backup
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path for the data_outputs folder
output_dir = os.path.join(script_dir, 'data_outputs')

# Create the data_outputs directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define the full path for the output CSV file
output_csv_path = os.path.join(output_dir, 'population_counts_cleaned.csv')

# Save the DataFrame to CSV
population_counts_v3.to_csv(
    output_csv_path,
    index=False # Important: Prevents Pandas from writing the DataFrame index as a column
)

print(f"DataFrame successfully saved to: {output_csv_path}")