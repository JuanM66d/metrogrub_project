import requests
from google.cloud import bigquery

def ingest_chicago_demographics(request):
    client = bigquery.Client()

    api_url = "https://data.cityofchicago.org/resource/85cm-7uqa.json"

    response = requests.get(api_url)

    if response.status_code != 200:
        return f"Failed to fetch data: {response.status_code}"

    data = response.json()
    print(f"Fetched {len(data)} records from API.")

    rows_to_insert = []
    for item in data:
        rows_to_insert.append({
            "geography_type": item.get("geography_type"),
            "year": item.get("year"),
            "zip_code": item.get("geography"),
            "population_total": item.get("population_total"),
            "population_0_to_17": item.get("population_age_0_17"),
            "population_18_to_29": item.get("population_age_18_29"),
            "population_30_to_39": item.get("population_age_30_39"),
            "population_40_to_49": item.get("population_age_40_49"),
            "population_50_to_59": item.get("population_age_50_59"),
            "population_60_to_69": item.get("population_age_60_69"),
            "population_70_to_79": item.get("population_age_70_79"),
            "population_80": item.get("population_age_80"),
            "population_female": item.get("population_female"),
            "population_male": item.get("population_male"),
            "population_latinx": item.get("population_latinx"),
            "population_asian": item.get("population_asian_non_latinx"),
            "population_black": item.get("population_black_non_latinx"),
            "population_white": item.get("population_white_non_latinx"),
            "population_other": item.get("population_other_race_non"),
            "record_id": item.get("record_id"),
        })

    print(f"Prepared {len(rows_to_insert)} rows for insertion.")

    # Define table IDs
    project = "purple-25-gradient-20250605"
    dataset = "chicago_demographics"
    main_table_id = f"{project}.{dataset}.population_counts"
    staging_table_id = f"{project}.{dataset}.population_counts_staging"

    try:
        # Delete staging table if it exists
        client.delete_table(staging_table_id, not_found_ok=True)
        print(f"Deleted existing staging table {staging_table_id} (if it existed).")

        # Create an empty staging table with the same schema as main table
        schema = client.get_table(main_table_id).schema
        table = bigquery.Table(staging_table_id, schema=schema)
        client.create_table(table)
        print(f"Created empty staging table {staging_table_id} with copied schema.")

        # Ensure table is ready before inserting
        for attempt in range(5):
            try:
                client.get_table(staging_table_id)
                print(f"Staging table {staging_table_id} is now ready.")
                break
            except Exception as e:
                print(f"Waiting for staging table to be ready (attempt {attempt + 1}/5)...")
                time.sleep(2)
        else:
            return f"Staging table {staging_table_id} not found after waiting."

        # Insert rows into staging table in batches
        batch_size = 1000
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i+batch_size]
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
