# Chicago Foot Traffic Data Generator

This Python script generates synthetic yearly average foot traffic data for locations across Chicago. It uses real-world geospatial zoning data to classify city blocks into residential, commercial, or high-traffic transit areas, making the generated data more realistic.

The script fetches raw location and zoning data from a **Google Cloud Storage (GCS)** bucket and uploads the final, generated dataset to a **Google BigQuery** table.

---
## How It Works

1.  **Data Loading**: The script securely loads two essential files from your specified GCS bucket:
    * `chicago_traffic_counts_raw.csv`: A CSV file containing latitude and longitude coordinates.
    * `Chicago_Zoning_Data.geojson`: A GeoJSON file with Chicago's zoning polygons.
2.  **Data Generation**: For each coordinate, the script determines its zoning category (e.g., Residential, Commercial, Downtown).
3.  **Traffic Simulation**: Based on the zoning category, it generates a realistic yearly average foot traffic number within predefined ranges.
4.  **BigQuery Upload**: The final dataset, containing latitude, longitude, and the generated foot traffic average, is uploaded to a specified BigQuery table.

---
## Requirements

Go to Service Account and use key for service account "FootTrafficGen" and then run this command

export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service_account_key.json"

You need Python 3 and the following libraries. You can install them all using `pip` after making virtual env:

```bash
python3 -m venv .venv 
source .venv/bin/activate
pip install pandas geopandas shapely google-cloud-storage gcsfs pandas-gbq
```

Then to run app do (Must be in venv and key authenticated within env):

python3 metrogrub_project/scripts/foot_traffic_data/main.py


