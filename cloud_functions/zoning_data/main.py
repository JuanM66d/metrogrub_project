import requests
import json
from google.cloud import bigquery

def ingest_chicago_zoning(request):
    client = bigquery.Client()

    base_api_url = "https://data.cityofchicago.org/resource/dj47-wfun.json"
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
                "geometry": json.dumps(item.get("the_geom")),  # stringify nested geojson
                "case_number": item.get("case_numbe"),
                "zoning_id": item.get("zoning_id"),
                "zone_type": item.get("zone_type"),
                "zone_class": item.get("zone_class"),
                "create_date": item.get("create_dat"),
                "edit_date": item.get("edit_date"),
                "edit_uid": item.get("edit_uid"),
                "pd_num": item.get("pd_num"),
                "shape_area": float(item.get("shape_area") or 0),
                "shape_len": float(item.get("shape_len") or 0),
                "objectid": item.get("objectid"),
                "globalid": item.get("globalid"),
                "override_r": item.get("override_r"),
            })

        offset += limit

        # Break early if fewer than limit records returned (end of dataset)
        if len(data) < limit:
            break

    print(f"Total records prepared for insertion: {len(all_rows)}.")

    table_id = "purple-25-gradient-20250605.chicago_zoning.zoning_data"

    # Insert in batches of 10,000 rows to avoid API insert limits
    batch_size = 1000
    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
            return f"Encountered errors while inserting rows: {errors}"

    print("Data successfully loaded into BigQuery.")
    return "Data successfully loaded into BigQuery."
