import requests
import json
from google.cloud import bigquery

def ingest_chicago_business_licenses(request):
    client = bigquery.Client()

    base_api_url = "https://data.cityofchicago.org/resource/uupf-x98q.json"
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
                "license_id": item.get("license_id"),
                "account_number": item.get("account_number"),
                "site_number": item.get("site_number"),
                "legal_name": item.get("legal_name"),
                "doing_business_as_name": item.get("doing_business_as_name"),
                "address": item.get("address"),
                "city": item.get("city"),
                "state": item.get("state"),
                "zip_code": item.get("zip_code"),
                "ward": item.get("ward"),
                "precinct": item.get("precinct"),
                "ward_precinct": item.get("ward_precinct"),
                "police_district": item.get("police_district"),
                "community_area": item.get("community_area"),
                "community_area_name": item.get("community_area_name"),
                "neighborhood": item.get("neighborhood"),
                "license_code": item.get("license_code"),
                "license_description": item.get("license_description"),
                "business_activity_id": item.get("business_activity_id"),
                "business_activity": item.get("business_activity"),
                "license_number": item.get("license_number"),
                "application_type": item.get("application_type"),
                "application_requirements_complete": item.get("application_requirements_complete"),
                "payment_date": item.get("payment_date"),
                "conditional_approval": item.get("conditional_approval"),
                "license_start_date": item.get("license_start_date"),
                "expiration_date": item.get("expiration_date"),
                "license_approved_for_issuance": item.get("license_approved_for_issuance"),
                "date_issued": item.get("date_issued"),
                "license_status": item.get("license_status"),
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
    dataset = "chicago_active_business_licenses"
    main_table_id = f"{project}.{dataset}.active_business_licenses"
    staging_table_id = f"{project}.{dataset}.active_business_licenses_staging"

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
