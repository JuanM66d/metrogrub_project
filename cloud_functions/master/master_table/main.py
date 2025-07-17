import os
import ast
import json
import pandas_gbq
import numpy as np
import pandas as pd
import geopandas as gpd

from google.cloud import storage
from google.cloud import bigquery
from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.wkt import loads as wkt_loads

def create_master_table(request):
    client = bigquery.Client()

    food_inspection_table = os.environ["FOOD_INSPECTIONS_TABLE"]
    food_license_table = os.environ["FOOD_LICENSES_TABLE"]
    divvy_stations_table = os.environ["DIVVY_STATIONS_TABLE"]
    population_counts_table = os.environ["POPULATION_COUNTS_TABLE"]
    zoning_data_table = os.environ["ZONING_DATA_TABLE"]
    bus_station_table = os.environ["BUS_STATIONS_TABLE"]
    foot_traffic_table = os.environ["FOOT_TRAFFIC_TABLE"]
    master_table = os.environ["OUTPUT_TABLE"]

    food_inspection_df = client.query(f"SELECT * FROM `{food_inspection_table}`").to_dataframe()
    food_license_df = client.query(f"SELECT * FROM `{food_license_table}`").to_dataframe()
    divvy_stations_df = client.query(f"SELECT * FROM `{divvy_stations_table}`").to_dataframe()
    population_counts_df = client.query(f"SELECT * FROM `{population_counts_table}`").to_dataframe()
    zoning_data_df = client.query(f"SELECT * FROM `{zoning_data_table}`").to_dataframe()
    bus_station_df = client.query(f"SELECT * FROM `{bus_station_table}`").to_dataframe()
    foot_traffic_df = client.query(f"SELECT * FROM `{foot_traffic_table}`").to_dataframe()


    print(f"Retrieved {len(food_inspection_df)} rows from {food_inspection_table}")
    print(f"Retrieved {len(food_license_df)} rows from {food_license_table}")
    print(f"Retrieved {len(divvy_stations_df)} rows from {divvy_stations_table}")
    print(f"Retrieved {len(population_counts_df)} rows from {population_counts_table}")
    print(f"Retrieved {len(zoning_data_df)} rows from {zoning_data_table}")
    print(f"Retrieved {len(bus_station_df)} rows from {bus_station_table}")
    print(f"Retrieved {len(foot_traffic_df)} rows from {foot_traffic_table}")


    # Add boolean col (this is help in looker filtering food/bus_stop/divvy_station if needed)
    food_license_df['is_food'] = 1
    food_license_df['is_business'] = 0
    food_license_df['is_bus_stop'] = 0
    food_license_df['is_divvy_station'] = 0

    bus_station_df['is_food'] = 0
    bus_station_df['is_business'] = 0
    bus_station_df['is_bus_stop'] = 1
    bus_station_df['is_divvy_station'] = 0

    divvy_stations_df['is_food'] = 0
    divvy_stations_df['is_business'] = 0
    divvy_stations_df['is_bus_stop'] = 0
    divvy_stations_df['is_divvy_station'] = 1
    divvy_stations_df = divvy_stations_df.drop(['status','location_type','location_coordinates'],axis=1)

    # food inspection data will already have their 'is_food' and 'is_business' columns set from the cleaning function
    food_inspection_df['is_bus_stop'] = 0
    food_inspection_df['is_divvy_station'] = 0

    # Append point type data sources together
    draft_df = pd.concat([food_license_df, food_inspection_df, bus_station_df, divvy_stations_df], ignore_index=True)
    # Fill missing 'location' with a placeholder WKT string
    draft_df['location'] = draft_df['location'].fillna("POINT(0 0)")
    # wrap the DataFrame into a GeoDataFrame that supports spatial joins, distance calculations, and exporting to BigQuery as a GEOGRAPHY column.
    draft_df['geometry'] = draft_df['location'].apply(wkt_loads)
    # Convert to GeoDataFrame
    combined_gdf = gpd.GeoDataFrame(draft_df, geometry='geometry', crs='EPSG:4326')


    # Convert geometry string to actual geometry objects, then convert to GeoDataFrame
    zoning_data_df['geometry'] = zoning_data_df['geometry'].apply(lambda x: shape(json.loads(x)))
    zoning_gdf = gpd.GeoDataFrame(zoning_data_df, geometry='geometry', crs='EPSG:4326')

    # Now we can perform a spatial join to combine the zoning data with the combined GeoDataFrame
    combined_gdf = gpd.sjoin(
        combined_gdf, 
        zoning_gdf[['geometry', 'zone_class']], 
        how='left', 
        predicate='within'
    )

    # Clean up zip_code formatting
    combined_gdf['zip_code'] = combined_gdf['zip_code'].astype(str).str.zfill(5)
    population_counts_df['zip_code'] = population_counts_df['zip_code'].astype(str).str.zfill(5)

    # Left merge so that rows with zip_code will have population_total attached
    combined_gdf = combined_gdf.merge(
        population_counts_df[['zip_code', 'population_total', 'population_18_to_29', 'population_30_to_39', 'population_40_to_49']],
        on='zip_code',
        how='left'
    )

    # Convert foot traffic to GeoDataFrame
    foot_traffic_df = foot_traffic_df.dropna(subset=['latitude', 'longitude'])
    foot_traffic_gdf = gpd.GeoDataFrame(
        foot_traffic_df,
        geometry=gpd.points_from_xy(foot_traffic_df['longitude'], foot_traffic_df['latitude']),
        crs='EPSG:4326'
    )

    # Convert both to numpy arrays for fast spatial search
    master_coords = np.array(list(combined_gdf.geometry.apply(lambda geom: (geom.x, geom.y))))
    traffic_coords = np.array(list(foot_traffic_gdf.geometry.apply(lambda geom: (geom.x, geom.y))))

    tree = cKDTree(traffic_coords)
    _, indices = tree.query(master_coords, k=1)  # k=1 for nearest

    # Assign the nearest foot traffic score
    combined_gdf['foot_traffic_score'] = foot_traffic_gdf.iloc[indices]['yearly_average_foot_traffic'].values

    # some final organization before upload
    combined_gdf = combined_gdf.drop(columns=['index_right', 
                                            'legal_name',
                                            'business_activity',
                                            'business_activity_id',
                                            'license_description',
                                            'facility_type',
                                            'city',
                                            'state',
                                            'bus_stop_id',
                                            'street',
                                            'cross_st',
                                            'divvy_station_id',
                                            ])

    column_order = [
        'is_food',
        'is_business',
        'license_id',
        'doing_business_as_name',
        'category',
        'fake_location_score',
        'foot_traffic_score',
        'zone_class',
        'location',
        'longitude',
        'latitude',
        'address',
        'zip_code',
        'is_bus_stop',
        'bus_stop',
        'is_divvy_station',
        'station_name',
        'total_docks',
        'population_total',
        'population_18_to_29',
        'population_30_to_39',
        'population_40_to_49',
        'geometry'
    ]

    combined_gdf = combined_gdf[column_order]

    # some final cleaning

    # Divide between businesses/restaurants and bus/divvy station
    to_clean = combined_gdf[combined_gdf['doing_business_as_name'].notna()]
    not_to_clean = combined_gdf[combined_gdf['doing_business_as_name'].isna()]

    # Deduplicate only the businesses/restaurants rows
    # this avoids removing the bus/divvy stations that dont have 'doing_business_as_name'
    to_clean = to_clean.drop_duplicates(subset=['doing_business_as_name', 'address'], keep='first')

    # Combine them back together
    final_gdf = pd.concat([to_clean, not_to_clean], ignore_index=True)
    
    # Define the job config
    job_config = bigquery.LoadJobConfig(
        autodetect=True,  # Automatically detects schema from DataFrame
        write_disposition="WRITE_TRUNCATE"  # Overwrites the table if it exists
    )

    # Upload the DataFrame to BigQuery
    job = client.load_table_from_dataframe(final_gdf, master_table, job_config=job_config)

    # Wait for the job to complete
    job.result()

    print(f"✅ Upload completed. {len(final_gdf)} rows written to {master_table}")
    return f"Successfully uploaded {len(final_gdf)} rows to BigQuery."
