import pandas as pd
import numpy as np
import geopandas as gp
from shapely.geometry import Point
import sys
import pandas_gbq # Import for BigQuery functionality

# Imports for Google Cloud Storage integration
from google.cloud import storage
import gcsfs

def get_block_type_from_zoning(latitude, longitude, zoning_gdf):
    """
    Determines the block type (0, 1, or 2) based on Chicago zoning data.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        zoning_gdf (geopandas.GeoDataFrame): The GeoDataFrame containing zoning polygons.

    Returns:
        int: block_type (0: Residential, 1: Commercial/Mixed, 2: High Commercial/Transit)
             or None if the point is outside any known zoning polygon.
    """
    point = Point(longitude, latitude) # Shapely uses (longitude, latitude)

    # Use a spatial index for faster lookups
    if not hasattr(zoning_gdf, 'sindex'):
        print("Generating spatial index for zoning data for faster processing...")
        zoning_gdf.sindex

    # Find potential matches using the spatial index
    possible_matches_index = list(zoning_gdf.sindex.intersection(point.bounds))
    possible_matches = zoning_gdf.iloc[possible_matches_index]
    
    # Iterate over the smaller subset of possible matches
    for idx, row in possible_matches.iterrows():
        if row.geometry.contains(point):
            zoning_class = row['zone_class'].strip() # Get the zoning classification

            if zoning_class.startswith('R'):
                return 0 # Residential
            elif zoning_class.startswith('B') or zoning_class.startswith('C'):
                return 1 # Business or Commercial
            elif zoning_class.startswith('D') or zoning_class.startswith('DC'):
                return 2 # Downtown, High Commercial/Transit
            elif zoning_class.startswith('M'):
                return 0 # Manufacturing, treat as low traffic
            return 1 # Default to general commercial if zone found but not mapped

    # If point is outside any known zoning polygon
    return None

def generate_yearly_average_foot_traffic(locations, zoning_gdf):
    """
    Generates synthetic yearly average foot traffic data for a list of locations,
    using zoning data to determine block type.

    Args:
        locations (list of tuples): A list of (latitude, longitude) tuples.
        zoning_gdf (geopandas.GeoDataFrame): GeoDataFrame with zoning polygons.

    Returns:
        pandas.DataFrame: A DataFrame with latitude, longitude, and yearly_average_foot_traffic.
    """
    data = []
    
    for lat, lon in locations:
        block_type = get_block_type_from_zoning(lat, lon, zoning_gdf)

        # If a location is outside a known zone, assign a random block type
        if block_type is None:
            block_type = np.random.choice([0, 1, 2], p=[0.5, 0.35, 0.15])

        # Generate random yearly average foot traffic based on block type
        if block_type == 2:  # Major Transit/High Commercial Hub
            yearly_average = np.random.randint(2000, 8001)
        elif block_type == 1:  # General Commercial/Mixed-Use
            yearly_average = np.random.randint(300, 1801)
        else:  # Residential or low-traffic Manufacturing
            yearly_average = np.random.randint(50, 501)
        
        # Add some additional randomness with a small probability of outliers
        if np.random.random() < 0.05:  # 5% chance of outlier
            if block_type == 2:
                yearly_average = np.random.randint(8000, 12001)
            elif block_type == 1:
                yearly_average = np.random.randint(1800, 3001)
            else:
                yearly_average = np.random.randint(500, 1001)

        data.append([lat, lon, yearly_average])

    print("Yearly average data generation complete.")
    df = pd.DataFrame(data, columns=['latitude', 'longitude', 'yearly_average_foot_traffic'])
    return df

if __name__ == '__main__':
    # --- Configuration ---
    # GCS Details
    BUCKET_NAME = 'foot_traffic_gen_resources'
    LOCATION_DATA_BLOB_NAME = 'chicago_traffic_counts_raw.csv'
    ZONING_DATA_BLOB_NAME = 'Chicago_Zoning_Data.geojson'
    
    # BigQuery Details
    BIGQUERY_PROJECT_ID = 'purple-25-gradient-20250605' # <-- IMPORTANT: UPDATE with your Project ID
    BIGQUERY_DATASET_ID = 'foot_traffic_chicago'
    BIGQUERY_TABLE_ID = 'yearly_average'


    # Initialize GCS filesystem
    gcs = gcsfs.GCSFileSystem()

    # --- Construct GCS Paths ---
    gcs_locations_path = f'gs://{BUCKET_NAME}/{LOCATION_DATA_BLOB_NAME}'
    gcs_zoning_path = f'gs://{BUCKET_NAME}/{ZONING_DATA_BLOB_NAME}'

    # --- Validate File Existence on GCS ---
    if not gcs.exists(gcs_locations_path):
        print(f"ERROR: Required location file not found in GCS bucket: {gcs_locations_path}")
        sys.exit(1)

    if not gcs.exists(gcs_zoning_path):
        print(f"ERROR: Required zoning file not found in GCS bucket: {gcs_zoning_path}")
        sys.exit(1)
        
    # --- Load Data Directly from GCS ---
    try:
        print(f"Loading location data from GCS: {gcs_locations_path}")
        with gcs.open(gcs_locations_path) as f:
            locations_df = pd.read_csv(f)
        print("Successfully loaded location data.")

        print(f"Loading zoning data from GCS: {gcs_zoning_path}")
        chicago_zoning_gdf = gp.read_file(gcs_zoning_path)
        print("Successfully loaded zoning data.")

    except Exception as e:
        print(f"An unexpected error occurred while loading data from GCS: {e}")
        sys.exit(1)

    # --- Data Cleaning and Preparation ---
    locations_df = locations_df[['Latitude', 'Longitude']].round(4).copy()
    locations_df.dropna(inplace=True)
    locations_df.drop_duplicates(inplace=True)
    
    chicago_fine_grained_blocks = list(locations_df.itertuples(index=False, name=None))

    # --- Generate Foot Traffic Data ---
    foot_traffic_df = generate_yearly_average_foot_traffic(
        chicago_fine_grained_blocks, 
        zoning_gdf=chicago_zoning_gdf
    )

    # --- Save Output to BigQuery ---
    destination_table = f"{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}"
    print(f"\nWriting {len(foot_traffic_df)} records to BigQuery table: {BIGQUERY_PROJECT_ID}.{destination_table}")

    try:
        foot_traffic_df.to_gbq(
            destination_table=destination_table,
            project_id=BIGQUERY_PROJECT_ID,
            if_exists='replace', # Options: 'fail', 'replace', 'append'
            progress_bar=True
        )
        print("Successfully wrote data to BigQuery.")

    except Exception as e:
        print(f"An error occurred while writing to BigQuery: {e}")
        sys.exit(1)
    