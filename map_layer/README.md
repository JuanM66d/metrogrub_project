HOW TO CREATE CUSTOM MAP LAYER FOR LOCSTION ZONE MAP

1. After master table has been created, go to BigQuery and run saved query:
    - "02 Grid Zone Creation Query"

2. Download created/updated table as a csv file
    - After running the saved query, go to the grid_zone table
    - This will be found under master_table_final.grid_zones
    - Export the table to cloud storage as a csv file
    - Locate the exported file (will be stored in the bucket that you select to store it in)
    - Download the file locally and upload to the 'map_layer' directory in this project
    - Make sure you name it 'grid_zone.csv'

3. Run the main.py script in the map_layer directory
    - This will generate or update the 'zones_polygon.json' file

4. Go to https://geojson.io/
    - Copy all of the contents inside of 'zones_polygon.json'
    - While in the geojson.io website, paste into the 'json' text editor the contents of 'zones_polygon.json'
    - This will generate the custom grid map in the webiste

5. Download as topojson file
    - In the geojson.io website, click on 'save' then 'topojson'
    - You will now have a map.topojson file

6. Navigate to your lookML model
    - Copy the map.topojson into the same directorty as the lookML model you are using for looker.
    - In the .model file, create a custom map layer.
    - Should look like this example:
        
        map_layer: location_zones {
            file: "map.topojson"
            format: "topojson"
            property_key: "zone_id"
        }

    - Notice the 'property_key: zone_id'
    - This is how the zones are identified and visualized by looker.
    - This was added by the script we ran earlier.

7. Visualize the map and data
    - To view the map and the corresponding data for each zone, make sure to explore the 'grid_zones' view
    - The property_key 'zone_id' will match each zone with its respective data