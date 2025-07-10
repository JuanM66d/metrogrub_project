import requests
import json
from google.cloud import bigquery

def ingest_chicago_food_inspections(request):
    client = bigquery.Client()

    base_api_url = "https://data.cityofchicago.org/resource/4ijn-s7e5.json"
    limit = 5000
    offset = 0
    all_rows = []

    while True:
        api_url = f"{base_api_url}?$limit={limit}&$offset={offset}"
        response = requests.get(api_url)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return f"Failed to fetch data: {response.status_code}"

        data = response.json()
        print(f"Fetched {len(data)} records from offset {offset}.")

        if not data:
            break  # No more data to fetch

        for item in data:
            all_rows.append({
                "inspection_id": item.get("inspection_id"),
                "dba_name": item.get("dba_name"),
                "aka_name": item.get("aka_name"),
                "license_": item.get("license_"),
                "facility_type": item.get("facility_type"),
                "risk": item.get("risk"),
                "address": item.get("address"),
                "city": item.get("city"),
                "state": item.get("state"),
                "zip": item.get("zip"),
                "inspection_date": item.get("inspection_date"),
                "inspection_type": item.get("inspection_type"),
                "results": item.get("results"),
                "violations": item.get("violations"),
                "latitude": float(item.get("latitude") or 0),
                "longitude": float(item.get("longitude") or 0),
                "location": json.dumps(item.get("location"))
            })
            
        offset += limit

        # Break early if fewer than limit records returned (end of dataset)
        if len(data) < limit:
            break

    print(f"Prepared {len(all_rows)} rows for insertion.")

    # Define table IDs
    project = "purple-25-gradient-20250605"
    dataset = "chicago_food_inspections"
    main_table_id = f"{project}.{dataset}.food_inspections_data"
    staging_table_id = f"{project}.{dataset}.food_inspections_data_staging"

    try:
        # Delete staging table if it exists
        client.delete_table(staging_table_id, not_found_ok=True)
        print(f"Deleted existing staging table {staging_table_id} (if it existed).")

        # Create an empty staging table with the same schema as main table
        schema = client.get_table(main_table_id).schema
        table = bigquery.Table(staging_table_id, schema=schema)
        client.create_table(table)
        print(f"Created empty staging table {staging_table_id} with copied schema.")

        # Insert rows into staging table in batches
        batch_size = 1000
        for i in range(0, len(all_rows), batch_size):
            batch = all_rows[i:i+batch_size]
            errors = client.insert_rows_json(staging_table_id, batch)
            if errors:
                print(f"Encountered errors while inserting rows into staging table: {errors}")
                return f"Encountered errors while inserting rows into staging table: {errors}"

        print("Data successfully loaded into staging table.")

        # Replace main table with staging table data (overwrite completely)
        replace_job = client.query(f"""
            CREATE OR REPLACE TABLE `{main_table_id}`
            AS SELECT * FROM `{staging_table_id}`
        """)
        replace_job.result()
        print(f"Main table {main_table_id} successfully replaced with staging table data.")

        # Delete staging table after swap
        client.delete_table(staging_table_id)
        print(f"Deleted staging table {staging_table_id} after successful replacement.")

        return "Data successfully replaced in main table using staging workflow."

    except Exception as e:
        print(f"Error during staging ingestion process: {e}")
        return f"Error during staging ingestion process: {e}"
