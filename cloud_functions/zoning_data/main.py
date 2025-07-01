import requests
import json
from google.cloud import bigquery

def ingest_chicago_zoning(request):
    client = bigquery.Client()

    api_url = "https://data.cityofchicago.org/resource/dj47-wfun.json"
    
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return f"Failed to fetch data: {response.status_code}"

    data = response.json()
    print(f"Fetched {len(data)} records from API.")

    rows_to_insert = []
    for item in data:
        rows_to_insert.append({
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

    print(f"Prepared {len(rows_to_insert)} rows for insertion.")

    table_id = "purple-25-gradient-20250605.chicago_zoning.zoning_data"

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if not errors:
        print("Data successfully loaded into BigQuery.")
        return "Data successfully loaded into BigQuery."
    else:
        print(f"Encountered errors while inserting rows: {errors}")
        return f"Encountered errors while inserting rows: {errors}"
