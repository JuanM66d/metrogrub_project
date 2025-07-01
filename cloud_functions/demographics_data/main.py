import requests
from google.cloud import bigquery

def ingest_chicago_demographics(request):
    client = bigquery.Client()

    api_url = "https://data.cityofchicago.org/resource/85cm-7uqa.json"

    response = requests.get(api_url)

    if response.status_code != 200:
        return f"Failed to fetch data: {response.status_code}"

    data = response.json()
    
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

    table_id = "purple-25-gradient-20250605.chicago_demographics.population_counts"

    errors = client.insert_rows_json(table_id, rows_to_insert)

    if not errors:
        return "Data successfully loaded into BigQuery."
    else:
        return f"Encountered errors while inserting rows: {errors}"
