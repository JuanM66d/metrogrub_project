import requests
from google.cloud import bigquery
import json

def ingest_cta_bus_station_data(request):
    client = bigquery.Client()

    base_api_url = "https://data.cityofchicago.org/resource/qs84-j7wh.json"
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
            coordinates = item.get("the_geom", {}).get("coordinates", [None, None])
            all_rows.append({
                "longitude": coordinates[0],
                "latitude": coordinates[1],
                "systemstop": item.get("systemstop"),
                "street": item.get("street"),
                "cross_st": item.get("cross_st"),
                "dir": item.get("dir"),
                "pos": item.get("pos"),
                "routesstpg": item.get("routesstpg"),
                "city": item.get("city"),
                "public_nam": item.get("public_nam")
        })
            
        offset += limit

        # Break early if fewer than limit records returned (end of dataset)
        if len(data) < limit:
            break

    print(f"Prepared {len(all_rows)} rows for insertion.")

    table_id = "purple-25-gradient-20250605.divvy_stations.divvy_stations_data"

    batch_size = 1000
    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
            return f"Encountered errors while inserting rows: {errors}"
                    
    print("Data successfully loaded into BigQuery.")
    return "Data successfully loaded into BigQuery."
