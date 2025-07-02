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

    table_id = "purple-25-gradient-20250605.chicago_food_inspections.food_inspections_data"

    batch_size = 1000
    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
            return f"Encountered errors while inserting rows: {errors}"
                    
    print("Data successfully loaded into BigQuery.")
    return "Data successfully loaded into BigQuery."
