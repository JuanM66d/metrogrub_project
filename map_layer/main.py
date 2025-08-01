import pandas as pd
import json
import ast

# Load your table (example from CSV or BigQuery)
df = pd.read_csv("grid_zone.csv")  # Or use BigQuery API to load

# Ensure geojson is parsed as a dictionary
def parse_geojson(geojson_str):
    try:
        return json.loads(geojson_str)
    except json.JSONDecodeError:
        # fallback if geojson_str is malformed (e.g., single quotes)
        return ast.literal_eval(geojson_str)

# Build the features list
features = []
for _, row in df.iterrows():
    geometry = parse_geojson(row['geojson'])
    feature = {
        "type": "Feature",
        "properties": {
            "zone_id": row["zone_id"]
        },
        "geometry": geometry
    }
    features.append(feature)

# Wrap into FeatureCollection
feature_collection = {
    "type": "FeatureCollection",
    "features": features
}

# Export to JSON file
with open("zones_polygons.json", "w") as f:
    json.dump(feature_collection, f, indent=2)
