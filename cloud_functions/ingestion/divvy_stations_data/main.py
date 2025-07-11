import requests
from google.cloud import bigquery
import json

def ingest_divvy_station_data(request):
    client = bigquery.Client()

    base_api_url = "https://data.cityofchicago.org/resource/bbyy-e7gq.json"
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
                "id": item.get("id"),
                "station_name": item.get("station_name"),
                "short_name": item.get("short_name"),
                "total_docks": item.get("total_docks"),
                "docks_in_service": item.get("docks_in_service"),
                "status": item.get("status"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "location_type": item.get("location", {}).get("type"),
                "location_coordinates": json.dumps(item.get("location", {}).get("coordinates"))
        })
            
        offset += limit

        # Break early if fewer than limit records returned (end of dataset)
        if len(data) < limit:
            break

    print(f"Prepared {len(all_rows)} rows for insertion.")

    # Define table IDs
    project = "purple-25-gradient-20250605"
    dataset = "divvy_stations"
    main_table_id = f"{project}.{dataset}.divvy_stations_data"
    staging_table_id = f"{project}.{dataset}.divvy_stations_data_staging"

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
