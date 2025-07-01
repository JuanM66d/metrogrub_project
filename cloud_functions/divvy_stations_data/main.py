import requests
from google.cloud import bigquery
import json

def ingest_divvy_station_data(request):
    client = bigquery.Client()

    api_url = "https://data.cityofchicago.org/resource/bbyy-e7gq.json"
    response = requests.get(api_url)
    if response.status_code != 200:
        return f"Failed to fetch data: {response.status_code}"

    data = response.json()
    print(f"Fetched {len(data)} records from API.")

    rows_to_insert = []
    for item in data:
        rows_to_insert.append({
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

    table_id = "purple-25-gradient-20250605.divvy_stations.divvy_stations_data"

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if not errors:
        print("Data successfully loaded into BigQuery.")
        return "Data successfully loaded into BigQuery."
    else:
        print(f"Encountered errors while inserting rows: {errors}")
        return f"Encountered errors while inserting rows: {errors}"
