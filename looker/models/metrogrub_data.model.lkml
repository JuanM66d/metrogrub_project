# Define the database connection to be used for this model.
connection: "purple_big_query"

# include all the views
include: "/looker/views/**/*.view.lkml"

# Datagroups define a caching policy for an Explore. To learn more,
# use the Quick Help panel on the right to see documentation.

datagroup: metrogrub_data_default_datagroup {
  # sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: metrogrub_data_default_datagroup

explore: master {
  group_label: "metrogrub_data"
  from: master_table_final_v3
}

explore: master_looker {
  group_label: "metrogrub_data"
  from: master_final_looker
}

explore: grid_zones {
  group_label: "metrogrub_data"
  from: grid_zones
}


map_layer: location_zones {
  file: "map.topojson"
  format: "topojson"
  property_key: "zone_id"
}
